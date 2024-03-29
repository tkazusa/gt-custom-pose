### ラベリング対象データ
Amazon S3 バケットにデータをアップロードすることでGround Truthのラベリングジョブが活用できるようになります。今回は、姿勢推定タスクのベンチマークに用いられる[MPII Human Pose Dataset](http://human-pose.mpi-inf.mpg.de/#download)(Simplified BSDライセンス)の一部を活用します。


### 入力のマニフェスト
ラベリングジョブのための入力データ内の各オブジェクトは、マニフェスの記述よって特定されアノテーション担当者に送信されます。
マニフェストファイル内の各行は、ラベル付けされる有効な JSON Lines オブジェクトと、その他のカスタムメタデータです。
入力データとマニフェストは S3 バケットに保存されます。マニフェスト内の各 JSON 行には以下が含まれています。

- 画像の S3 オブジェクト URI が含まれる source-ref JSON オブジェクト。
- テキストの S3 オブジェクト URI が含まれる text-file-s3-uri JSON オブジェクト。
- 追加のメタデータが含まれる metadata JSON オブジェクト。

下記は今回の入力マニフェストの例です。
```
{"source-ref": "<S3 image URI>"}
{"source-ref": "<S3 image URI>"}
{"source-ref": "<S3 image URI>"}
{"source-ref": "<S3 image URI>"}
```

このマニフェストに他の情報を追記して、Ground Truthが使うHTMLテンプレートに変数を渡すような場合もあります。詳細については、Amazon SageMaker 開発者ガイドの「[入力データ](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-data-input.html)」や[デモテンプレート: crowd-bounding-box を使用したイメージの注釈](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-custom-templates-step2-demo1.html)を参照してください。


### HTMLテンプレート
カスタムラベリングジョブでは定義済のテンプレートをカスタマイズして使う事が出来ます。
今回は"Keypoint"というHTMLテンプレートをカスタマイズして[template.html](https://github.com/tkazusa/gt-custom-pose/blob/master/web/template.html)を作成しました。


### プレラベリング Lambda関数
入力マニフェストエントリを処理して、Ground Truthのテンプレートエンジンにアノテーションデータやその他のを渡すために呼び出す[プレラベリング Lambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-preprocess.py)を準備します。

プレラベリング Lambda関数へ渡されるGround Truthからのリクエストは下記の様な形になります。

```
{
	"version": "2018-10-16",
	"labelingJobArn": "<labelingJobArn>",
	"dataObject": {
		"source-ref": "<S3 image URI>"
	}
}
```

今回は追加の処理を行わずにマニフェストからの情報をそのまま渡しています。HTMLテンプレートに入力するような変数がある場合は、この[Lambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-preprocess.py)で処理します。Ground Truthへのレスポンスは下記の様な形になります。

```
{
	"taskInput": {
		"taskObject": "<S3 image URI>"
	}
}
```


### ポストラベリング Lambda関数
ワーカーが全てのアノテーションタスクを完了したら、Ground Truth は結果を [ポストラベリング Lambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-postprocess.py) に送信します。
この Lambda は一般に、[注釈統合](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-annotation-consolidation.html)に使用されます。

受け取るリクエストオブジェクトは次のようになります。'payload.s3Uri'の中にはs3バケットのconsolidated_requestディレクトリの中にあるアノテーションデータへのパスが入っています。

```
{
	"version": "2018-10-16",
	"labelingJobArn": "<labelingJobArn>",
	"labelCategories": [
		"<string>"
	],
	"labelAttributeName": "<string>",
	"roleArn": "string",
	"payload": {
		"s3Uri": "<S3 image URI>"
	}
}
```


ポストラベリング Lambda関数がリクエストを受け取ると、それぞれのデータについてのアノテーションデータファイルを読み込み、統合する処理を実行します。
読み込まれるアノテーションデータファイルは次のような形になります。

```
[
	{
		"datasetObjectId": "1",
		"dataObject": {
			"s3Uri": "<S3 image URI>",
			"content": "<string>"
		},
		"annotations": [
			{
				"workerId": "<workId>",
				"annotationData": {
					"content": "<string>",
					"s3Uri": "<s3Uri>"
				}
			}
		]
	}
]
```

それぞれのデータオブジェクトに対してアノテーションが統合されるとポストラベリング Lambda関数からは下記のような配列がレスポンスとしてGround Truthへ渡されます。

```
[
	{
		"datasetObjectId": "1",
		"consolidatedAnnotation": {
			"content": {
				"<LabelingJobName>": {
					"workerId": "<workId>",
					"result": {
						"annotatedResult": {
							"inputImageProperties": {
								"height": 720,
								"width": 1280
							},
							"keypoints": [
								{
									"label": "<label>",
									"x": "int",
									"y": "int"
								},
								・
								・
								・
							]
						}
					}
					"labeledContent": {
						"s3Uri": "<s3Uri>"
					}
				}
			}
		}
	},
	・
	・
	・
]
```



最終的にs3バケットの'consolidated_response'ディレクトリに配置される注釈統合後のアノテーションデータは次のようになります。


```
[
	{
		"datasetObjectId": "1",
		"consolidatedAnnotation": {
			"content": {
				"<LabelingJobName>": {
					"workerId": "<workId>",
					"result": {
						"annotatedResult": {
							"inputImageProperties": {
								"height": 720,
								"width": 1280
							},
							"keypoints": [
								{
									"label": "<label>",
									"x": "int",
									"y": "int"
								},
								・
								・
								・
							]
						}
					}
					"labeledContent": {
						"s3Uri": "<s3Uri>"
					}
				}
			}
		}
	},
	・
	・
	・
]
```

## ラベリングジョブによる出力

SageMaker Ground Truthでラベリングジョブを実行すると、以上のプロセスとなります。最終的にS3バケットへは下記のような構成で出力がされます。

```
output
|_<LabelingJobName> 
    |_annotation-tool
    |   |_template.liquid      
    |_annotations
    |   |_consolidated_annotation
    |   |   |_consolidation-request
    |   |       |_iteration-1
    |   |           |_XXXXXXX.json 
    |   |   |_consolidated_response
    |   |       |_XXXXXXX.json 
    |   |
    |   |_intermediate
    |   |   |_anotations.json
    |   |   |_annotations.json-query.tmp
    |   |   |_annotations.json-sample
    |   |
    |   |_worker-response
    |       |_iteration-1
    |           |_0
    |               |_XXXXXXX.json
    |
    |_manifests
        |_output
            |_output.manifest
```

ラベリングジョブの全ての工程が完了するとそれぞれのデータについて`output.manifest`が出力されます。

```output.manifest
{
    "source-ref":"s3://gt-custom-labeling-pose/images/000030973.jpg",
    "<LabelingJobName>":{
        "workerId":"<workerId>",
        "result":{"annotatedResult":{"inputImageProperties":{"height":720,"width":1280},
        "keypoints":[{"label":"<Label>",<Cordinate>},・・・]
        }
    },
    "labeledContent":{
        "s3Uri":"<s3Uri>"}
    },
    "<LabelingJobName>-metadata":{
        "type":"groundtruth/custom",
        "job-name":"<LabelingJobName>",
        "human-annotated":"yes",
        "creation-date":"<date>"
    }
}
```

それぞれのワーカーのアノテーションについて詳細な管理がしたい場合は、`worker-response`に置かれているJSONファイルを活用すると良いでしょう。

```a.json
{
	"answers": [
		{
			"answerContent": {
				"annotatedResult": {
					"inputImageProperties": {
						"height": 720,
						"width": 1280
					},
					"keypoints": [
						{
							"label": "<Label>",
							"x": "int",
							"y": "int"
						}
					]
				}
			},
			"submissionTime": "<submittionTime>",
			"workerId": "<workId>"
		}
	]
}
```


# SageMaker Ground Truth カスタムラベリング 姿勢推定
## 概要
SageMaker Ground Truthでは前・後処理のLambda関数とラベリングツールのHTMLテンプレートを変更するとで、様々なタスクに対応することができます。
今回は組み込みラベリングツールにはない姿勢推定タスクに対するラベリングジョブを、カスタムテンプレートを活用して構築します。

## カスタムデータラベリングジョブの主なコンポーネント
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
{"source-ref": "<S3 image URI>", "animal": "horse"}
{"source-ref": "<S3 image URI>", "animal" : "bird"}
{"source-ref": "<S3 image URI>", "animal" : "dog"}
{"source-ref": "<S3 image URI>", "animal" : "cat"}
```

詳細については、Amazon SageMaker 開発者ガイドの「[入力データ](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-data-input.html)」を参照してください。


### HTMLテンプレート
カスタムラベリングジョブでは定義済のテンプレートをカスタマイズして使う事が出来ます。
今回は"Keypoint"というHTMLテンプレートをカスタマイズして[template.html](https://github.com/tkazusa/gt-custom-pose/blob/master/web/template.html)を作成しました。



### プレラベリング Lambda関数
入力マニフェストエントリを処理して、Ground Truthのテンプレートエンジンに情報を渡すために呼び出す[プレラベリング Lambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-preprocess.py)を準備します。

プレラベリング Lambda関数へ渡されるリクエストは下記の様な形になります。

```
{
    "version": "2018-10-16",
    "labelingJobArn": <labelingJobArn>
    "dataObject" : {
        "source-ref": "s3://mybucket/myimage.png"
    }
}
```

レスポンスは下記の様な形になります。
```
{
    "taskInput": <json object>,
    "isHumanAnnotationRequired": <boolean> # Optional
}
```


### ポストラベリング Lambda関数
ワーカーがタスクを完了したら、Ground Truth は結果を [ポストラベリング Lambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-postprocess.py) に送信します。
この Lambda は一般に、[注釈統合](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-annotation-consolidation.html)に使用されます。

受け取るリクエストオブジェクトは次のようになります。
```
{
    "version": "2018-10-16",
    "labelingJobArn": <labelingJobArn>,
    "labelCategories": [<string>],
    "labelAttributeName": <string>,
    "roleArn" : "string",
    "payload": {
        "s3Uri": <string>
    }
 }
```


ポストラベリング Lambda関数がリクエストを受け取ると、それぞれのデータについてのアノテーションデータファイルを読み込み、統合する処理を実行します。

S3に保存されているアノテーションデータファイルは次のようになります。

```
[
    {
        "datasetObjectId": <string>,
        "dataObject": {
            "s3Uri": <string>,
            "content": <string>
        },
        "annotations": [{
            "workerId": <string>,
            "annotationData": {
                "content": <string>,
                "s3Uri": <string>
            }
       }]
    }
]
```


それぞれのデータオブジェクトに対してアノテーションが統合されるとポストラベリング Lambda関数からは下記のようなレスポンスがGround Truthにひつようい　になります。
```
[
   {        
        "datasetObjectId": <string>,
        "consolidatedAnnotation": {
            "content": {
                "<labelattributename>": {
                    # ... label content
                }
            }
        }
    },
   {        
        "datasetObjectId": <string>,
        "consolidatedAnnotation": {
            "content": {
                "<labelattributename>": {
                    # ... label content
                }
            }
        }
    }
    .
    .
    .
]
```

最終的にジョブの統合マニフェストにあるエントリは次のようになります。
```
{  "source-ref"/"source" : "<s3uri or content>", 
   "<labelAttributeName>": {
        # ... label content from you
    },   
   "<labelAttributeName>-metadata": { # This will be added by Ground Truth
        "job_name": <labelingJobName>,
        "type": "groundTruth/custom",
        "human-annotated": "yes", 
        "creation_date": <date> # Timestamp of when received from Post-labeling Lambda
    }
}
```


## 参考資料
- [Amazon SageMaker Ground Truth を使ったカスタムデータラベリングワークフローの構築](https://aws.amazon.com/jp/blogs/news/build-a-custom-data-labeling-workflow-with-amazon-sagemaker-ground-truth/)
- [AWS Lambda を使用した処理](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-custom-templates-step3.html)

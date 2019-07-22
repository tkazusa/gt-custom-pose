# SageMaker Ground Truth カスタムラベリング 姿勢推定
## 概要
SageMaker Ground Truthでは前・後処理のLambda関数とラベリングツールのHTMLテンプレートを変更するとで、様々なタスクに対応することができます。
今回は組み込みラベリングツールにはない姿勢推定タスクに対するラベリングジョブを、カスタムテンプレートを活用して構築します。

## カスタムデータラベリングジョブの主なコンポーネント
### 1. HTMLテンプレート
- カスタムラベリングジョブでは定義済のテンプレートをカスタマイズして使う事が出来ます。
- 今回は"Keypoint"というHTMLテンプレートをカスタマイズして[template.html](https://github.com/tkazusa/gt-custom-pose/blob/master/web/template.html)を作成しました。

### 2. ラベリング対象のデータ
- ラベリングするデータです。S3に保存します。

### 3. 入力のマニフェスト
- Ground TruthでどのS3上にあるどのラベリング対象データを使うか、メタデータは何かなどのを記載したファイル。
- S3上に保存します。
- プレラベリング Lambda関数が活用します。

### 4. プレラベリング Lambda関数
- 入力マニフェストエントリを処理して、Ground Truthのテンプレートエンジンに情報を渡すために呼び出す[プレラベリング Lambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-preprocess.py)を準備します。

### 5. ポストラベリング Lambda関数
- ワーカーがタスクを完了したら、Ground Truth は結果を [ポストラベリング Lambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-postprocess.py) に送信します。
- この Lambda は一般に、[注釈統合](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-annotation-consolidation.html)に使用されます。

## 【WIP】本ハンズオンの手順 


## 参考資料
- [Amazon SageMaker Ground Truth を使ったカスタムデータラベリングワークフローの構築](https://aws.amazon.com/jp/blogs/news/build-a-custom-data-labeling-workflow-with-amazon-sagemaker-ground-truth/)
- [AWS Lambda を使用した処理](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-custom-templates-step3.html)

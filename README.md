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
### ワークフォースのセットアップ
本ハンズオンではご自身でアノテーションを実施するため、プライベートワークフォースを作成します。
- [こちら](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-getting-started-step3.html)を参考にご自身のEメールアドレスを使用して、ワークフォースのメンバーに登録して下さい。

### データのS3へのアップロード
- `こちら`から画像データを手元にダウンロード下さい。
- 新しくS3バケットを作成し、画像データをディレクトリごとアップロード下さい。
- この際、作成するs3バケットは今回活用するSageMaker Ground Truthと同じリージョンをしてい下さい。

### ラベリングジョブの作成
- Ground Truth ラベリングジョブから「ラベリングジョブの作成」を選択します。
#### ジョブの概要
- ジョブ名は重複を避けて入力して下さい。
- 「マニフェストファイルを作成します」をクリックします。データセットの場所へは先程データをアップロードしたS3バケットを指定し、データタイプはイメージを選択します。
- 出力データセットの場所は先程データをアップロードしたS3バケットを指定します。
- IAMロールは「create new role」をクリック、「指定するS3バケット」では「任意のS3バケット」を選択し、ロールを作成します。
#### タスクのタイプ
- タスクのタイプ中のTask categoryではカスタムを選択します。
#### ワーカー
- TODO

#### カスタムラベリングタスクの設定
- テンプレートでは`Keypoint`を選択します。
- 表示されているHTMLを削除し、準備してある[HTMLテンプレート](https://github.com/tkazusa/gt-custom-pose/blob/master/web/template.html)へ書き換えます。

#### プレラベリング Lambda関数の準備
- AWS Lambdaコンソール、関数の作成をクリックしプレラベリングLambda関数を作成します。
- 「一から作成」を選択、関数名に`sagemaker-gt-preprocess`を入力、ランタイムに`Python3.7`を選択した上で`関数の作成`をクリックします。
- `lambda_function.py`の内容を削除し、準備してある[プレラベリングLambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-preprocess.py)へ書き換えます。
- `基本設定`の`タイムアウト`の項目を1分0秒へ変更します。

#### ポストラベリング Lambda関数の準備
- プレラベリングLambda関数と同様にAWS Lambdaコンソール、関数の作成をクリックしポストラベリングLambda関数を作成します。
- 「一から作成」を選択、関数名に`sagemaker-gt-postprocess`を入力、ランタイムに`Python3.7`を選択した上で`関数の作成`をクリックします。
- `lambda_function.py`の内容を削除し、準備してある[ポストラベリングLambda関数](https://github.com/tkazusa/gt-custom-pose/blob/master/server/processing/sagemaker-gt-postprocess.py)へ書き換えます。
- `実行ロール`パネルの中で
- `基本設定`の`タイムアウト`の項目を1分0秒へ変更します。
- 




### ポストラベリングLamb
- timeoutは60sec
- Lambda を作成するためのコンソールページで [Execution role (実行ロール)] パネルまでスクロールします。[AWS ポリシーテンプレートから新しいロールを作成] を選択します。ロール名に`gt-custom-keypoint-post`と入力します。[ポリシーテンプレート] ドロップダウンから [Amazon S3 object read-only permissions (Amazon S3 オブジェクトの読み取り専用アクセス権限)] を選択します。Lambda を保存すると、ロールが保存されて選択されます。

## 参考資料
- [Amazon SageMaker Ground Truth を使ったカスタムデータラベリングワークフローの構築](https://aws.amazon.com/jp/blogs/news/build-a-custom-data-labeling-workflow-with-amazon-sagemaker-ground-truth/)
- [Build your own custom labeling workflow using SageMaker Ground Truth(Github repository)](https://github.com/nitinaws/gt-custom-workflow.git)
- [AWS Lambda を使用した処理](https://docs.aws.amazon.com/ja_jp/sagemaker/latest/dg/sms-custom-templates-step3.html)

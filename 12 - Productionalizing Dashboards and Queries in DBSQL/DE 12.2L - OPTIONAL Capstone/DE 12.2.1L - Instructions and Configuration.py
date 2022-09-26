# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md <i18n value="01f3c782-1973-4a69-812a-7f9721099941"/>
## レイクハウスでのエンドツーエンドETL（End-to-End ETL in the Lakehouse）

このノートブックでは、コース全体で学習した概念をまとめて、データパイプラインの例を完成させます。

以下は、この演習を正常に完了するために必要なスキルとタスクの（包括的でない）リストです。
* Databricksノートブックを使用してSQLとPythonでクエリを作成する
* データベース、テーブル、およびビューの作成と変更
* マルチホップアーキテクチャでの増分データ処理にAuto LoaderとSpark構造化ストリーミングを使用する
* Delta Live TablesのSQL構文を使用する
* 継続的な処理のためにDelta Live Tablesのパイプラインを設定する
* Databricksジョブsを使用して、Reposに保存されているノートブックからタスクに対してオーケストレーションを実行する
* Databricksジョブの時系列スケジュールを設定する
* Databricks SQLでクエリを定義する
* Databricks SQLでビジュアライゼーションを作成する
* Databricks SQLダッシュボードを定義してメトリックと結果を確認する

# COMMAND ----------

# MAGIC %md <i18n value="f9cf3bbc-aa6a-45c2-9d26-a3785e350e1f"/>
## セットアップを実行する（Run Setup）
次のセルを実行して、このラボに関連しているすべてのデータベースとディレクトリをリセットします。

# COMMAND ----------

# MAGIC %run ../../Includes/Classroom-Setup-12.2.1L

# COMMAND ----------

# MAGIC %md <i18n value="3fe92b6e-3e10-4771-8eef-8f4b060dd48f"/>
## 初期データの配置（Land Initial Data）
先に進む前に、データを用いてランディングゾーンをシードします。

# COMMAND ----------

DA.data_factory.load()

# COMMAND ----------

# MAGIC %md <i18n value="806818f8-e931-45ba-b86f-d65cdf76f215"/>
## DLTパイプラインを作成し構成する（Create and Configure a DLT Pipeline）
**注**：ここでの手順とDLTを使用した以前のラボでの手順の主な違いは、この場合、**プロダクション**モードで**連続**に実行するためにパイプラインを設定することです。

# COMMAND ----------

DA.print_pipeline_config()

# COMMAND ----------

# MAGIC %md <i18n value="e1663032-caa8-4b99-af1a-3ab27deaf130"/>
手順は、次の通りです。
1. サイドバーの**ワークフロー**をクリックします
1. **Delta Live Tables**タブを選択します。
1. **パイプラインを作成**をクリックします。
1. **パイプライン名**を入力します。名前は一意である必要があるため、上記のセルに記載されている**Pipeline Name**使用することをおすすめします。
1. **ノートブックライブラリ**では、上記のセルに記載されているノートブックを探して選択します。
1. **構成**の下に, 3つの構成パラメータを追加します：
   * **構成を追加**をクリックし, "key"を**spark.master**、 "value"を **local[\*]** にします。
   * **構成を追加**をクリックし, "key"を**datasets_path**、 "value"を上記セルに記載されている値にします。
   * **構成を追加**をクリックし, "key"を**source**、 "value"を上記セルに記載されている値にします。
1. **ターゲット**フィールドに、上記のセルで記載されているデータベースの名前を指定します。<br/> データベースの名前は **`da_<name>_<hash>_dewd_cap_12`** というパターンに従っているはずです。
1. **ストレージの場所**フィールドに、上記で出力されている通りディレクトリをコピーします
1. **Pipeline Mode**では、**連続**を選択します。
1. **オートスケーリングを有効化**ボックスのチェックを外します。(**オートスケーリングを有効化**がUIになければ、**Cluster mode**から**Fixed size**を選択します)
1. ワーカーの数を **`0`** （０個）に設定します。
1. **Photonアクセラレータを使用**をチェックします。
1. **作成**をクリックします
1. UIが更新されたら、**開発**モードから**プロダクション**モードに変更します

これにより、インフラストラクチャの展開が開始されます。

# COMMAND ----------

DA.validate_pipeline_config()

# COMMAND ----------

# MAGIC %md <i18n value="6c8bd13c-938a-4283-b15a-bc1a598fb070"/>
## ノートブックジョブをスケジュールする（Schedule a Notebook Job）

DLTパイプラインは、データが到着するとすぐに処理するように設定されています。

この機能が実際に動作していることを確認できるように、毎分新しいデータのバッチを配置するようにノートブックをスケジュールします。

開始する前に、次のセルを実行して、このステップで使用される値を取得します。

# COMMAND ----------

DA.print_job_config()

# COMMAND ----------

# MAGIC %md <i18n value="df989e07-97d4-4a34-9729-fad02399a908"/>
手順は、次の通りです。
1. Databricksの左側のナビゲーションバーを使って、ワークフローに移動します。
1. **ジョブ**を選択します。
1. 青色の**ジョブ作成**ボタンをクリックします
1. タスクを設定します：
    1. タスク名として**Land-Data**と入力します
    1. **種類**から**ノートブック**を選択します。
    1. **Path**に上記セルに記載されている**Notebook Path**を選択します
    1. **クラスター**のドロップダウンから**既存の多目的クラスター**の下にあるクラスタを選択します
    1. **作成**をクリックします
1. 画面の左上でジョブ（タスクではなく）を **`Land-Data`** （デフォルトの値）から前のセルに記載されている**Job Name**に変更します。

<img src="https://files.training.databricks.com/images/icon_note_24.png" /> **注**：汎用クラスタを選択する際、All-purposeコンピュートとして請求される警告が表示されます。 本番環境のジョブは常に、ワークロードにサイズを合わせた新しいジョブクラスタに対してスケジュールしたほうが良いです。こうしたほうが、費用を抑えられます。

# COMMAND ----------

# MAGIC %md <i18n value="3994f3ee-e335-48c7-8770-64e1ef0dfab7"/>
## ジョブの時系列のスケジュールを設定する（Set a Chronological Schedule for your Job）

手順は、次の通りです。
1. **スケジュール**をクリックします。
1. **スケジュールのタイプ**を **手動（一時停止）** から **スケジュール済み** に変更すると、cronスケジューリングUIが表示されます。
1. スケジュールの更新間隔を**毎2** **分**に設定します
1. **保存**をクリックします

**注**：必要に応じて、**今すぐ実行**をクリックして最初の実行をトリガーするか、次の1分が経過するまで待って、スケジュールが正常に機能することを確認します。

# COMMAND ----------

DA.validate_job_config()

# COMMAND ----------

# MAGIC %md <i18n value="30df4ffa-22b9-4e2c-b8d8-54aa09a8d4ed"/>
## DBSQLを使用して照会するためのDLTイベントメトリックを登録する（Register DLT Event Metrics for Querying with DBSQL）

次のセルは、DBSQLでクエリを実行するためにDLTイベントログをターゲットデータベースに登録するSQL文を出力します。

DBSQLクエリエディタで出力コードを実行して、これらのテーブルとビューを登録します。

それぞれを調べて、ログに記録されたイベントメトリックをメモします。

# COMMAND ----------

DA.generate_register_dlt_event_metrics_sql()

# COMMAND ----------

# MAGIC %md <i18n value="e035ddc7-4af9-4e9c-81f8-530e8db7c504"/>
## ゴールドテーブルでクエリを定義する（Define a Query on the Gold Table）

**daily_patient_avg**テーブルは、新しいデータのバッチがDLTパイプラインを介して処理されるたびに自動的に更新されます。 このテーブルに対してクエリが実行されるたびに、DBSQLは新しいバージョンがあるかどうかを確認し、利用可能な最新バージョンから結果を取得します。

次のセルを実行して、データベース名でクエリを出力します。 これをDBSQLクエリとして保存します。

# COMMAND ----------

DA.generate_daily_patient_avg()

# COMMAND ----------

# MAGIC %md <i18n value="679db36c-b257-4248-b2fe-56b85099d0b9"/>
## 折れ線グラフのビジュアライゼーションを追加する（Add a Line Plot Visualization）

時間の経過に伴う患者の平均の傾向を追跡するには、折れ線グラフを作成して新しいダッシュボードに追加します。

次の設定で折れ線グラフを作成します。
* **X列**:  **`date`** 
* **Y列**:  **`avg_heartrate`** 
* **Group By**:  **`name`** 

このビジュアライゼーションをダッシュボードに追加します。

# COMMAND ----------

# MAGIC %md <i18n value="7351e179-68f8-4091-a6ee-647974f010ce"/>
## データ処理の進捗状況を追跡する（Track Data Processing Progress）

以下のコードは、DLTイベントログから **`flow_name`** 、 **`timestamp`** 、 **`num_output_rows`**  を抽出します。

このクエリをDBSQLに保存してから、次を示す棒グラフのビジュアライゼーションを定義します。
* **X列**:  **`timestamp`** 
* **Y列**:  **`num_output_rows`** 
* **Group By**:  **`flow_name`** 

ダッシュボードにビジュアライゼーションを追加します。

# COMMAND ----------

DA.generate_visualization_query()

# COMMAND ----------

# MAGIC %md <i18n value="5f94b102-d42e-40f1-8253-c14cbf86d717"/>
## ダッシュボードを更新して結果を追跡する（Refresh your Dashboard and Track Results）

上記のジョブでスケジュールされた**Land-Data**ノートブックには、12バッチのデータがあり、それぞれが患者の少量のサンプルの1ヶ月分の記録を表しています。 手順に従って設定されているとすれば、これらのデータのバッチがすべてトリガーされて処理されるまでに20分強かかります（Databricksジョブが2分ごとに実行されるようにスケジュールされ、データのバッチは最初の取り込み後パイプラインを介して非常に迅速に処理されます）。

ダッシュボードを更新し、ビジュアライゼーションを確認して、処理されたデータのバッチ数を確認します。 （ここで概説されている手順に従った場合、DLTメトリックによって追跡されている異なるフロー更新が12件あるはずです。） すべてのソースデータがまだ処理されていない場合は、Databricks Jobs UIに戻って、追加のバッチを手動でトリガーできます。

# COMMAND ----------

# MAGIC %md <i18n value="b61bf387-2c1b-4ae6-8968-c4189beb477f"/>
すべてを設定したら、ノートブックでラボの最後の部分 \[DE 12.2.4L - 最終ステップ\]($./DE 12.2.4L - 最終ステップ）に進むことができます

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2022 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>

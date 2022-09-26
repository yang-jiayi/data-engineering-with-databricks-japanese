# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md <i18n value="1fb32f72-2ccc-4206-98d9-907287fc3262"/>
# Delta Live TablesUIの使用（Using the Delta Live Tables UI）

このデモではDLT UIについて見ていきます。


## 学習目標（Learning Objectives）
このレッスンでは、以下のことが学べます。
* DLTパイプラインをデプロイする
* 結果DAGを調べる
* パイプラインの更新を実行する
* メトリックを見る

# COMMAND ----------

# MAGIC %md <i18n value="c950ed75-9a93-4340-a82c-e00505222d15"/>
## セットアップを実行する（Run Setup）

以下のセルは、このデモをリセットするために構成されています。

# COMMAND ----------

# MAGIC %run ../../Includes/Classroom-Setup-08.1.1

# COMMAND ----------

# MAGIC %md <i18n value="0a719ade-b4b5-49b5-89bf-8fc2b0b7d63c"/>
以下のセルを実行して、次の構成段階で使用する値を出力します。

# COMMAND ----------

DA.print_pipeline_config()

# COMMAND ----------

# MAGIC %md <i18n value="71b010a3-80be-4909-9b44-6f68029f16c0"/>
## パイプラインを作成し構成する（Create and Configure a Pipeline）

このセクションでは、コースウェアに付属しているノートブックを使ってパイプラインを構築します。 次のレッスンでは、ノートブックの内容について見ていきます。

1. サイドバーの**ワークフロー**ボタンをクリックします。
1. **Delta Live Tables**タブを選択します。
1. **パイプラインを作成**をクリックします。
1. **製品エディション**は**Advanced**のままにします。
1. **パイプライン名**を入力します。これらの名前は一意である必要があるため、上記のセルに記載されている **`Pipeline Name`** を使用することをおすすめします。
1. **ノートブックライブラリ**では、ナビゲーターを使って上記のノートブックを探して選択します。
   * このドキュメントは標準のDatabricksノートブックですが、SQL構文はDLTテーブル宣言に特化しています。
   * 次のエクササイズでは、構文について見ていきます。
1. **構成**に、二つのパラメータを追加します。
   * **構成を追加**をクリックし, "key"を**spark.master**、"value"を **local[\*]** にします。
   * **構成を追加**をクリックし, "key"を**datasets_path**、"value"を上のセルに提供した値にします。
1. **ターゲット**に、上記のセルに提供したデータベースの名前を指定します。<br/> データベースの名前は、 **`da_<name>_<hash>_dewd_dlt_demo_81`** というパターンに従っているはずです。
   * このフィールドは任意です。指定しなかった場合、テーブルはメタストアに登録されませんが、引き続きDBFSでは使用できます。 このオプションに関して詳しく知りたい場合は、こちらの<a href="https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-user-guide.html#publish-tables" target="_blank">ドキュメント</a>を参考にしてください。
1. **ストレージの場所**フィールドには、上記のセルの隣に表示されている **`Storage location`** を入力しましょう。
   * この任意フィールドを使うことで、ユーザーはログ、テーブル、およびその他のパイプラインの実行に関連する情報を保管する場所が指定できます。
   * 指定しない場合、DLTが自動的にディレクトリを生成します。
1. **パイプラインモード**では、**トリガー**を選択します。
   * このフィールドでは、パイプラインの実行方法を指定します。
   * **トリガー**パイプラインは一度だけ実行され、次の手動またはスケジュールされた更新まではシャットダウンします。
   * **連続**パイプラインは継続的に実行され、新しいデータが到着するとそのデータを取り込みます。 レイテンシとコスト要件に基づいてモードを選択してください。
1. **Pipeline Mode**に**Triggered**を選択します。
1. **オートスケールを有効化**ボックスのチェックを外し、ワーカーの数を **`0`** （0個）に設定します。
　 (UIに**オートスケールを有効化**がなければ、**Cluster mode**から**Fixed size*を選択します)
   * 先ほど構成に追加したspark.masterに合わせてシングルモドのクラスタが作成されます。
1. **Photonアクセラレータを使用**をチェックします。
   * **オートスケールを有効化**、**ワーカーの最小数**、**ワーカーの最大数**はパイプラインをクラスタ処理する際の基盤となるワーカー構成を制御します。 このDBU試算は、インタラクティブクラスタを構成した時に得られる試算と似ていることに注意してください。
1. **作成**をクリックします。

# COMMAND ----------

# ANSWER

# This function is provided for students who do not 
# want to work through the exercise of creating the pipeline.
DA.create_pipeline()

# COMMAND ----------

DA.validate_pipeline_config()

# COMMAND ----------

# MAGIC %md <i18n value="a7e4b2fc-83a1-4509-8269-9a4c5791de21"/>
## パイプラインを実行する（Run a Pipeline）

パイプラインを構築したら、そのパイプラインを実行します。

1. **開発**を選択し、開発モードでパイプラインを実行します。
  * 開発モードでは、（実行の度に新しいクラスタを作成するのではなく）クラスタを再利用し再試行を無効にすることで、より迅速なインタラクティブ開発を可能にします。
  * この機能に関して詳しく知りたい場合は、こちらの<a href="https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-user-guide.html#optimize-execution" target="_blank">ドキュメント</a>を参考にしてください。
2. **開始**をクリックします。

クラスタが用意されている間、最初の実行には数分程度の時間が掛かります。

その後の実行では、速度が急激に速くなります。

# COMMAND ----------

# ANSWER

# This function is provided to start the pipeline and  
# block until it has completed, canceled or failed
DA.start_pipeline()

# COMMAND ----------

# MAGIC %md <i18n value="4b92f93e-7a7f-4169-a1d2-9df3ac440674"/>
## DAGを調べる（Exploring the DAG）

パイプラインが完了すると、実行フローがグラフ化されます。

テーブルを選択すると詳細を確認できます。

**sales_orders_cleaned**を選択します。 **データ品質**セクションで報告されている結果に注目してください。 このフローではデータの期待値が宣言されているため、それらのメトリックがここで追跡されます。 出力に違反しているレコードを含むように制限を宣言しているため、レコードが削除されることはありません。 この詳細は次のエクササイズで扱います。

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2022 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>

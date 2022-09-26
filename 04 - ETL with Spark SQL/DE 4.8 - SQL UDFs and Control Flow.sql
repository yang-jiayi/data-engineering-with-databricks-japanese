-- Databricks notebook source
-- MAGIC %md-sandbox
-- MAGIC 
-- MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
-- MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
-- MAGIC </div>

-- COMMAND ----------

-- MAGIC %md <i18n value="931bf77d-810b-4930-b45c-b00c184029a0"/>
# SQLのUDFと制御流れ（SQL UDFs and Control Flow）

DatabricksはDBR 9.1以降に、SQLでネイティブに登録できる、ユーザーによって定義された関数（UDF）のサポートを追加しました。

この機能を使用すると、SQLロジックのカスタムな組み合わせを関数としてデータベースに登録できます。これにより、これらのメソッドは、DatabricksでSQLを実行できる場所であれば再利用できます。 これらの関数は、Spark SQLを直接活用し、カスタムロジックを大きなデータセットに適用する際にSparkの最適化をすべて維持します。

このノートブックでは、まずはこれらのメソッドを簡単に紹介します。次に、再利用可能なカスタムの制御流れのロジックを構築するために、このロジックを **`CASE`**  /  **`WHEN`** 句と組み合わせる方法を学びます。

## 学習目標（Learning Objectives）
このレッスンでは、以下のことが学べます。
* SQL UDFの定義と登録
* SQL UDFの共有で使用するセキュリティモデルを説明する
* SQLコードで **`CASE`**  /  **`WHEN`** 文を使用する
* カスタムの制御流れのためにSQL UDFで **`CASE`**  /  **`WHEN`** 文を活用する

-- COMMAND ----------

-- MAGIC %md <i18n value="df80ac46-fb12-44ed-bb37-dcc5a4d73d4a"/>
## セットアップ（Setup）
次のセルを実行して、環境をセットアップします。

-- COMMAND ----------

-- MAGIC %run ../Includes/Classroom-Setup-04.8

-- COMMAND ----------

-- MAGIC %md <i18n value="f4fec594-3cd7-43c9-b88e-3ccd3a99c6be"/>
## 簡単なデータセットを作成する（Create a Simple Dataset）

このノートブックでは、ここにテンポラリビューとして登録されている次のデータセットを扱います。

-- COMMAND ----------

CREATE OR REPLACE TEMPORARY VIEW foods(food) AS VALUES
("beef"),
("beans"),
("potatoes"),
("bread");

SELECT * FROM foods

-- COMMAND ----------

-- MAGIC %md <i18n value="65577a77-c917-441c-895b-8ba146c837ff"/>
## SQL UDF
SQL UDFには少なくとも、関数名、任意のパラメーター、戻り値の型、いくつかのカスタムロジックが必要です。

以下の簡単な関数である **`yelling`** は **`text`** というの1つのパラメーターを取ります。 この関数は、最後に3つのはてなマークがついている全ての文字が大文字の文字列を返します。

-- COMMAND ----------

CREATE OR REPLACE FUNCTION yelling(text STRING)
RETURNS STRING
RETURN concat(upper(text), "!!!")

-- COMMAND ----------

-- MAGIC %md <i18n value="4cffc92d-3133-45ba-97c8-b0bc4c9e419b"/>
この関数が列にあるすべての値にSpark処理エンジン内で平行に適用されることにご注意ください。 SQL UDFを使用すると、Databricksでの実行に最適化されているカスタムロジックを効率的に定義できます。

-- COMMAND ----------

SELECT yelling(food) FROM foods

-- COMMAND ----------

-- MAGIC %md <i18n value="e1749d08-2186-4e1c-9214-18c8199388af"/>
## SQL UDFの範囲と権限（Scoping and Permissions of SQL UDFs）

SQL UDFは（ノートブック、DBSQLクエリ、およびジョブなど）実行環境の間で保持されるのでご注意ください。

関数の定義を表示すると、登録された場所および予想入力と戻り値についての基本情報を確認できます。

-- COMMAND ----------

DESCRIBE FUNCTION yelling

-- COMMAND ----------

-- MAGIC %md <i18n value="6a6eb6c6-ffc8-49d9-a39a-a5e1f6c230af"/>
DESCRIBE EXTENDEDを実行するとさらに多くの情報を表示できます。

関数の説明の下にある **`Body`** フィールドは、関数自体の中で使用されているSQLロジックを表します。

-- COMMAND ----------

DESCRIBE FUNCTION EXTENDED yelling

-- COMMAND ----------

-- MAGIC %md <i18n value="a31a4ad1-5608-4bfb-aae4-a411fe460385"/>
SQL UDFsはメタストア内のオブジェクトとして存在し、データベース、テーブル、ビューと同じテーブルACLによって管理されます。

SQL UDFを使用するのにユーザーは、関数に対して **`USAGE`** と **`SELECT`** の権限を持っている必要があります。

-- COMMAND ----------

-- MAGIC %md <i18n value="155c70b7-ed5e-47d2-9832-963aa18f3869"/>
## CASE/WHEN

SQLの標準統語構造である **`CASE`**  /  **`WHEN`** を使用すると、テーブルの内容によって結果が異なる複数の条件文を評価できます。

繰り返しますが、すべての評価がSparkでネイティブに実行されるため、並行処理に最適化されています。

-- COMMAND ----------

SELECT *,
  CASE 
    WHEN food = "beans" THEN "I love beans"
    WHEN food = "potatoes" THEN "My favorite vegetable is potatoes"
    WHEN food <> "beef" THEN concat("Do you have any good recipes for ", food ,"?")
    ELSE concat("I don't eat ", food)
  END
FROM foods

-- COMMAND ----------

-- MAGIC %md <i18n value="50bc0847-94d2-4167-befe-66e42b287ad0"/>
## 簡単な流れ制御の関数（Simple Control Flow Functions）

SQL UDFを **`CASE `**  /  **`WHEN `** 句の形式で制御流れと組み合わせると、SQL内のワークロードの制御流れの実行が最適化されます。

ここでは、前のロジックを、SQLを実行できる場所ならどこでも再利用できる関数で包む方法を示します。

-- COMMAND ----------

CREATE FUNCTION foods_i_like(food STRING)
RETURNS STRING
RETURN CASE 
  WHEN food = "beans" THEN "I love beans"
  WHEN food = "potatoes" THEN "My favorite vegetable is potatoes"
  WHEN food <> "beef" THEN concat("Do you have any good recipes for ", food ,"?")
  ELSE concat("I don't eat ", food)
END;

-- COMMAND ----------

-- MAGIC %md <i18n value="05cb00cc-097c-4607-8738-ab4353536dda"/>
このメソッドをこのデータに使用すると、予想した結果が得られます。

-- COMMAND ----------

SELECT foods_i_like(food) FROM foods

-- COMMAND ----------

-- MAGIC %md <i18n value="24ee3267-9ddb-4cf5-9081-273502f5252a"/>
ここに用意されている例は簡単な文字列のメソッドですが、この基本原理を使用してカスタムの計算およびSpark SQLでのネイティブの実行のためのロジックを追加できます。

特に、多くの定義済み手順もしくはカスタムで定義された式を持つシステムからユーザーを移行させている企業の場合、SQL UDFを使用すると、一般的な報告および分析のクエリに必要な複雑なロジックを少数のユーザーが定義できるようになります。

-- COMMAND ----------

-- MAGIC %md <i18n value="9405ddea-5fb0-4168-9fd2-2b462d5809d9"/>
次のセルを実行して、このレッスンに関連するテーブルとファイルを削除してください。

-- COMMAND ----------

-- MAGIC %python
-- MAGIC DA.cleanup()

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC &copy; 2022 Databricks, Inc. All rights reserved.<br/>
-- MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
-- MAGIC <br/>
-- MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="https://help.databricks.com/">Support</a>

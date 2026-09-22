# Step 2 — Import `diabetes_clean.csv` into `STG_DIABETES`

Load the cleaned CSV into the staging table using the **SQL Developer Import
Data wizard** (no manual INSERT for 236k rows).

## Steps in Oracle SQL Developer

1. Run `01_create_tables.sql` first so `STG_DIABETES` exists.
2. In the **Connections** panel, expand your connection → **Tables**.
3. Right-click **`STG_DIABETES`** → **Import Data...**
4. Choose the file **`diabetes_clean.csv`**.
   - Format: **CSV**
   - Header: **check "Header"** (first row has column names)
   - Encoding: UTF-8
5. **Import Method:** choose **Insert**.
6. **Column mapping:** the CSV column order already matches the table:
   `Diabetes_012, HighBP, HighChol, CholCheck, BMI, Smoker, Stroke,
   HeartDiseaseorAttack, PhysActivity, Fruits, Veggies, HvyAlcoholConsump,
   AnyHealthcare, NoDocbcCost, GenHlth, MentHlth, PhysHlth, DiffWalk, Sex,
   Age, Education, Income`
   → map each CSV column to the matching staging column.
7. Click **Finish**. Wait for the load to complete.

## Verify the load

```sql
SELECT COUNT(*) FROM stg_diabetes;          -- expect 236378
SELECT * FROM stg_diabetes FETCH FIRST 5 ROWS ONLY;
```

If the count is 236378, continue with `03_populate.sql`.

> Tip: if the wizard is slow, increase the batch size in the wizard's
> last step, or use SQL*Loader with the same column order.

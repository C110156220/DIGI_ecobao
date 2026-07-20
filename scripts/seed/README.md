# scripts/seed — 開發用資料填充腳本 (Dev seeding scripts)

一次性的開發 / 展示用腳本，透過 `pymysql` 直接對本機 MySQL 寫入假資料，
方便在開發環境快速產生大量測試用會員與店家。**僅供本機開發使用，切勿在正式環境執行。**

| 檔案 | 用途 |
| --- | --- |
| `random_account.py` | 批次建立測試會員（`data_maintenance_memberp` / `data_maintenance_member`），密碼以 Django `make_password` 雜湊。 |
| `random_add.py` | 批次建立測試店家（`data_maintenance_store`），隨機產生名稱 / 類型 / 地區。 |

## 使用前須知

- 這些腳本內的資料庫連線（host / port / user / password / database）目前為
  **本機 MySQL 預設值**（`localhost:3306`、`root`、空密碼、`ecobao`）。
  執行前請自行改成你自己的連線資訊，切勿沿用於任何非本機環境。
- 先完成 Django migrations（`python manage.py migrate`）產生資料表後再執行。
- 需安裝 `pymysql`。
- 產生的資料皆為 `test*` 前綴的假資料，可安全清除。

## 執行

```bash
# 於專案根目錄、且已設定好資料庫連線後
python scripts/seed/random_account.py
python scripts/seed/random_add.py
```

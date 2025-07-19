# superset_wrapper/wrapper.py (Platform-Enhanced Superset Wrapper)
import requests
import jwt
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import re

class SupersetAutoDashboard:
    def __init__(self, superset_url, username, password):
        self.session = requests.Session()
        self.base_url = superset_url.rstrip('/')
        self.token = self._login(username, password)
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _login(self, username, password):
        res = self.session.post(f"{self.base_url}/api/v1/security/login", json={"username": username, "password": password})
        res.raise_for_status()
        return res.json()["access_token"]

    def create_database(self, sqlalchemy_uri, db_name="auto_db"):
        payload = {
            "database_name": db_name,
            "sqlalchemy_uri": sqlalchemy_uri,
            "expose_in_sqllab": True
        }
        res = self.session.post(f"{self.base_url}/api/v1/database/", json=payload)
        res.raise_for_status()
        return res.json()["id"]

    def get_or_create_dataset(self, table_name, db_id, schema="dbo"):
        res = self.session.get(f"{self.base_url}/api/v1/dataset/?q=(table_name:{table_name})")
        data = res.json().get("result", [])
        if data:
            return data[0]["id"]
        return self.create_dataset(table_name, db_id, schema)

    def create_dataset(self, table_name, database_id, schema="dbo"):
        payload = {
            "database": database_id,
            "schema": schema,
            "table_name": table_name,
            "dataset_name": f"{table_name}_dataset"
        }
        res = self.session.post(f"{self.base_url}/api/v1/dataset/", json=payload)
        res.raise_for_status()
        return res.json()["id"]

    def get_existing_chart(self, slice_name):
        res = self.session.get(f"{self.base_url}/api/v1/chart/?q=(slice_name:{slice_name})")
        data = res.json().get("result", [])
        if data:
            return data[0]["id"]
        return None

    def create_chart(self, dataset_id, viz_type="bar", metric="count", groupby="id"):
        slice_name = f"AutoChart_{groupby}_{metric}"
        existing = self.get_existing_chart(slice_name)
        if existing:
            return existing

        payload = {
            "slice_name": slice_name,
            "viz_type": viz_type,
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": {
                "metrics": [metric],
                "groupby": [groupby],
                "time_range": "No filter"
            }
        }
        res = self.session.post(f"{self.base_url}/api/v1/chart/", json=payload)
        res.raise_for_status()
        return res.json()["id"]

    def create_dashboard(self, dashboard_title, chart_ids):
        payload = {
            "dashboard_title": dashboard_title,
            "charts": chart_ids
        }
        res = self.session.post(f"{self.base_url}/api/v1/dashboard/", json=payload)
        res.raise_for_status()
        return res.json()["id"]

    def get_dashboard_url(self, dashboard_id):
        return f"{self.base_url}/superset/dashboard/{dashboard_id}/"

    def generate_guest_token(self, dashboard_id, role="Gamma", username="embed_user"):
        secret = "your-super-secret-key"  # Set in superset_config.py JWT_SECRET
        payload = {
            "user": {
                "username": username,
                "first_name": "Embed",
                "last_name": "User",
                "roles": [role]
            },
            "resources": [{"type": "dashboard", "id": dashboard_id}],
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, secret, algorithm="HS256")

    def introspect_table(self, sqlalchemy_uri, table_name):
        try:
            engine = sqlalchemy.create_engine(sqlalchemy_uri)
            insp = sqlalchemy.inspect(engine)
            columns = insp.get_columns(table_name)
            return [{"name": col["name"], "type": str(col["type"]).upper()} for col in columns]
        except SQLAlchemyError as e:
            print(f"Error inspecting table {table_name}: {e}")
            return []

    def prompt_to_config(self, prompt, schema):
        prompt = prompt.lower()
        groupby = next((c["name"] for c in schema if any(k in c["name"] for k in ["region", "category", "state", "name"])), schema[0]["name"])
        metric_col = next((c["name"] for c in schema if any(k in c["name"] for k in ["amount", "sales", "revenue", "price"]) and ("INT" in c["type"] or "FLOAT" in c["type"])), None)
        metric = f"sum({metric_col})" if metric_col else "count(*)"

        if "trend" in prompt or "over time" in prompt or re.search(r"by (month|day|year)", prompt):
            viz_type = "line"
        elif "compare" in prompt:
            viz_type = "bar"
        elif "distribution" in prompt or "split" in prompt:
            viz_type = "pie"
        else:
            viz_type = "bar"

        return {
            "groupby": groupby,
            "metric": metric,
            "viz_type": viz_type
        }

    def deploy_from_prompt(self, sqlalchemy_uri, table_name, prompt):
        schema = self.introspect_table(sqlalchemy_uri, table_name)
        if not schema:
            return {"error": f"Failed to introspect table '{table_name}'"}
        config = self.prompt_to_config(prompt, schema)
        db_id = self.create_database(sqlalchemy_uri)
        dataset_id = self.get_or_create_dataset(table_name, db_id)
        chart_id = self.create_chart(dataset_id, **config)
        dash_id = self.create_dashboard(f"{table_name}_auto_dash", [chart_id])
        token = self.generate_guest_token(dash_id)
        return {
            "dashboard_id": dash_id,
            "url": self.get_dashboard_url(dash_id),
            "token": token,
            "config_used": config
        }

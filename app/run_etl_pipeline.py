from app.main import etl_pipeline

etl_pipeline(governments_subset=["Belgium"], write_to_s3=False)

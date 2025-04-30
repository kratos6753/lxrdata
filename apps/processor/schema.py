import pyarrow as pa

schema = pa.schema([
  pa.field('campaign_id', pa.string()),
  pa.field('date', pa.date32()),
  pa.field('spend', pa.float64()), # ad spend
  pa.field('impressions', pa.int64()),
  pa.field('dimensions', pa.struct([
    pa.field('country', pa.string()),
    pa.field('device', pa.string())
  ]))
])


# new column additons can be done by updating schema

# updated_schema = schema.append(pa.field('clicks', pa.int64()))

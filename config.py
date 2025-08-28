import os

# Use external URL for local development, internal URL for Render
if 'RENDER' in os.environ:  # Render sets this environment variable
    DATABASE_URI = 'postgresql://arch_db_qus8_user:xuCBzlaZUNHeWRcQHS09AXwkampaabAu@dpg-d2o05eje5dus739hkcv0-a/arch_db_qus8'
else:
    DATABASE_URI = 'postgresql://arch_db_qus8_user:xuCBzlaZUNHeWRcQHS09AXwkampaabAu@dpg-d2o05eje5dus739hkcv0-a.oregon-postgres.render.com/arch_db_qus8?sslmode=require'
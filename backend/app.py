from fastapi import FastAPI

app = FastAPI(title='Biometric Liveness Detection API')

@app.get('/health')
def health_check():
    return {'status': 'ok'}

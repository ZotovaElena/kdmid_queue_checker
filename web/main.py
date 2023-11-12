from fastapi import FastAPI

from web import router

def create_app():
    app = FastAPI()
    app.include_router(router.api)

    # https://github.com/tiangolo/fastapi/issues/1921
    @app.get('/')
    def root():
        return {'message': 'Main Page for routing'}

    return app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(create_app(), host='0.0.0.0', port=8000)
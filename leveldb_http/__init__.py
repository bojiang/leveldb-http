# encoding: utf-8
# pylint: disable=E0211
import functools
import json
from aiohttp import web
import plyvel


class Const:
    APP_NAME = "leveldb_http"
    STORE_PATH = 'run/db'


@functools.lru_cache(maxsize=10000, typed=True)
def get_db(name, path=Const.STORE_PATH):
    full_path = f'{path}/{name}'
    from pathlib import Path
    db_path = Path(full_path)
    if not db_path.is_dir():
        db_path.mkdir(parents=True, exist_ok=True)
    print(f'db <{name}> connected')
    return plyvel.DB(full_path, create_if_missing=True)


class Controller:
    @classmethod
    async def read_entity(cls, request):
        namespace = request.match_info.get('namespace', '')
        db = get_db(namespace)

        ids = request.rel_url.query.get('ids', '')
        if ids:
            values = [db.get(bytes(i.strip(), 'utf8')) for i in ids.split(',')]
            values = [v and v.decode('utf8') or v for v in values]
            return web.HTTPOk(text=json.dumps(values), content_type="text/json")
        start_id = request.rel_url.query.get('start', '')
        stop_id = request.rel_url.query.get('stop', '')
        limit = request.rel_url.query.get('limit', '')

        if start_id and stop_id:
            start = bytes(start_id, 'utf8')
            stop = bytes(stop_id, 'utf8')
            if start < stop:
                values = [(k, v) for k, v in db.iterator(start=start, stop=stop)]
            else:
                values = [(k, v) for k, v in
                          db.iterator(start=stop, stop=start, reverse=True,
                                      include_start=False, include_stop=True)]

            values = [(k.decode('utf8'), v and v.decode('utf8') or v) for k, v in values]
            return web.HTTPOk(text=json.dumps(values), content_type="text/json")

        if (start_id or stop_id) and limit and int(limit):
            limit = int(limit)
            if start_id:
                start = bytes(start_id, 'utf8')
                iterator = db.iterator(start=start)
            else:
                stop = bytes(stop_id, 'utf8')
                iterator = db.iterator(stop=stop, reverse=True, include_stop=True)

            values = []
            for k, v in iterator:
                values.append((k, v))
                if len(values) >= limit:
                    break
            values = [(k.decode('utf8'), v and v.decode('utf8') or v) for k, v in values]
            return web.HTTPOk(text=json.dumps(values), content_type="text/json")


        return web.HTTPBadRequest()

    @classmethod
    async def put_entity(cls, request):

        namespace = request.match_info.get('namespace', '')
        data = await request.post()

        db = get_db(namespace)
        with db.write_batch() as wb:
            for k, v in data.items():
                wb.put(bytes(k, 'utf8'), bytes(v, 'utf8'))
        return web.HTTPOk()

    @classmethod
    def serve_app(cls, port=80, host="0.0.0.0", debug=False):
        app = web.Application()
        app.add_routes([
            web.get('/{namespace}', cls.read_entity),
            web.post('/{namespace}', cls.put_entity),
        ])
        web.run_app(app, port=port, host=host)


if __name__ == '__main__':
    Controller.serve_app(debug=True, port=8080, host="127.0.0.1")

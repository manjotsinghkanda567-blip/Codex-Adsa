from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .database import connect, init_db
from .schemas import DeviceIn, ConnectionIn, DFSIn, ReachabilityIn
from .graph import adjacency, dfs, path, components

app=FastAPI(title='Network Connection Analyzer API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup(): init_db()

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(status_code=422,content={'detail':exc.errors()})

def rows(db,sql,args=()):return [dict(x) for x in db.execute(sql,args).fetchall()]
def require_device(db,id):
    r=db.execute('SELECT * FROM devices WHERE id=?',(id,)).fetchone()
    if not r: raise HTTPException(404,detail=f'Device {id} not found')
    return r
def check_unique(db,field,value,exclude=None):
    q=f'SELECT id FROM devices WHERE {field}=? COLLATE NOCASE';args=[value]
    if exclude is not None:q+=' AND id<>?';args.append(exclude)
    if db.execute(q,args).fetchone():raise HTTPException(409,detail=f'{field.replace("_"," ").title()} already exists')

@app.get('/api/devices')
def get_devices():
    with connect() as db:return rows(db,'SELECT * FROM devices ORDER BY id')
@app.get('/api/devices/{device_id}')
def get_device(device_id:int):
    with connect() as db:return dict(require_device(db,device_id))
@app.post('/api/devices',status_code=201)
def create_device(payload:DeviceIn):
    data=payload.model_dump()
    with connect() as db:
        check_unique(db,'name',data['name']);check_unique(db,'ip_address',data['ip_address'])
        cur=db.execute('INSERT INTO devices(name,ip_address,mac_address,status,connected_website,x,y) VALUES(?,?,?,?,?,?,?)',(data['name'],data['ip_address'],data['mac_address'],data['status'],data['connected_website'],data['x'],data['y']))
        return dict(require_device(db,cur.lastrowid))
@app.put('/api/devices/{device_id}')
def update_device(device_id:int,payload:DeviceIn):
    d=payload.model_dump()
    with connect() as db:
        require_device(db,device_id);check_unique(db,'name',d['name'],device_id);check_unique(db,'ip_address',d['ip_address'],device_id)
        db.execute("UPDATE devices SET name=?,ip_address=?,mac_address=?,status=?,connected_website=?,x=COALESCE(?,x),y=COALESCE(?,y),updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",(d['name'],d['ip_address'],d['mac_address'],d['status'],d['connected_website'],d['x'],d['y'],device_id))
        return dict(require_device(db,device_id))
@app.delete('/api/devices/{device_id}',status_code=204)
def delete_device(device_id:int):
    with connect() as db:require_device(db,device_id);db.execute('DELETE FROM devices WHERE id=?',(device_id,))

@app.get('/api/connections')
def get_connections():
    with connect() as db:return rows(db,'SELECT * FROM connections ORDER BY id')
@app.post('/api/connections',status_code=201)
def create_connection(payload:ConnectionIn):
    a,b=payload.source_device_id,payload.target_device_id
    if a==b:raise HTTPException(400,detail='A device cannot connect to itself')
    lo,hi=sorted((a,b))
    with connect() as db:
        require_device(db,a);require_device(db,b)
        if db.execute('SELECT 1 FROM connections WHERE source_device_id=? AND target_device_id=?',(lo,hi)).fetchone():raise HTTPException(409,detail='Connection already exists')
        cur=db.execute('INSERT INTO connections(source_device_id,target_device_id) VALUES(?,?)',(lo,hi))
        return dict(db.execute('SELECT * FROM connections WHERE id=?',(cur.lastrowid,)).fetchone())
@app.delete('/api/connections/{connection_id}',status_code=204)
def delete_connection(connection_id:int):
    with connect() as db:
        if not db.execute('SELECT 1 FROM connections WHERE id=?',(connection_id,)).fetchone():raise HTTPException(404,detail='Connection not found')
        db.execute('DELETE FROM connections WHERE id=?',(connection_id,))

@app.get('/api/stats')
def stats():
    with connect() as db:
        n=db.execute('SELECT COUNT(*) FROM devices').fetchone()[0];on=db.execute("SELECT COUNT(*) FROM devices WHERE status='online'").fetchone()[0];c=db.execute('SELECT COUNT(*) FROM connections').fetchone()[0]
        return {'total_devices':n,'online_devices':on,'offline_devices':n-on,'total_connections':c}
@app.get('/api/graph')
def get_graph():
    with connect() as db:
        return {'nodes':rows(db,'SELECT * FROM devices ORDER BY id'),'edges':rows(db,'SELECT * FROM connections ORDER BY id')}
def graph_data(db):
    ds=rows(db,'SELECT * FROM devices ORDER BY id');cs=rows(db,'SELECT * FROM connections ORDER BY id')
    return ds,cs,adjacency(ds,cs)
@app.post('/api/graph/dfs')
def graph_dfs(payload:DFSIn):
    with connect() as db:
        ds,cs,g=graph_data(db)
        if payload.start_device_id not in g:raise HTTPException(404,detail=f'Device {payload.start_device_id} not found')
        return dfs(g,payload.start_device_id)
@app.post('/api/graph/reachability')
def graph_reach(payload:ReachabilityIn):
    with connect() as db:
        ds,cs,g=graph_data(db)
        for i in (payload.source_device_id,payload.target_device_id):
            if i not in g:raise HTTPException(404,detail=f'Device {i} not found')
        p=path(g,payload.source_device_id,payload.target_device_id)
        return {'reachable':p is not None,'path':p or []}
@app.get('/api/graph/components')
def graph_components():
    with connect() as db:
        ds,cs,g=graph_data(db);groups=components(g)
        return {'component_count':len(groups),'components':groups}

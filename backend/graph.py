def adjacency(devices, connections):
    graph={int(d['id']):set() for d in devices}
    for c in connections:
        a,b=int(c['source_device_id']),int(c['target_device_id'])
        graph[a].add(b); graph[b].add(a)
    return graph

def dfs(graph,start):
    if start not in graph: return None
    seen={start}; order=[start]; tree=[]; stack=[(start,iter(sorted(graph[start])))]
    while stack:
        node,it=stack[-1]
        try: nxt=next(it)
        except StopIteration: stack.pop(); continue
        if nxt not in seen:
            seen.add(nxt); order.append(nxt); tree.append({'source_device_id':node,'target_device_id':nxt}); stack.append((nxt,iter(sorted(graph[nxt]))))
    return {'start_device_id':start,'traversal_order':order,'tree_edges':tree}

def path(graph,source,target):
    if source not in graph or target not in graph: return None
    parents={source:None}; stack=[source]
    while stack:
        n=stack.pop()
        if n==target: break
        for m in sorted(graph[n],reverse=True):
            if m not in parents: parents[m]=n; stack.append(m)
    if target not in parents:return None
    out=[]; n=target
    while n is not None:out.append(n);n=parents[n]
    return list(reversed(out))

def components(graph):
    seen=set(); groups=[]
    for start in sorted(graph):
        if start in seen:continue
        order=[]; stack=[start];seen.add(start)
        while stack:
            n=stack.pop();order.append(n)
            for m in sorted(graph[n],reverse=True):
                if m not in seen:seen.add(m);stack.append(m)
        groups.append(sorted(order))
    return groups

from flask import Flask, render_template, request
import grpc
import other98_pb2
import other98_pb2_grpc

app = Flask(__name__)

channel = grpc.insecure_channel('104.248.239.78:50051')
stub = other98_pb2_grpc.TheOther98Stub(channel)

def get_feed(stub, postTags: [str], page_id:str='', page_size:int=20, handle: str=''):
    print(f"get_feed tags={postTags}")
    grpc_request = other98_pb2.FeedRequest()
    grpc_request.postTags.extend(postTags)
    grpc_request.pageId = page_id
    grpc_request.pageSize = page_size
    grpc_request.authToken = handle
    return stub.GetFeed(grpc_request)

def get_post(stub, idstring: str, userhandle: str):
    getRequest = other98_pb2.GetRequest()
    getRequest.value = idstring
    getRequest.authToken = userhandle
    return stub.GetPost(getRequest)

def populate_database(stub):
    return stub.PopulateDatabase(other98_pb2.Void())

def serveFeed(type="forum"):
    global stub
    page = request.args.get('page', '')
    user = request.args.get('user', '')
    resp = get_feed(stub, postTags=[type], page_id=page, handle=user)
    posts = resp.postFeedViews
    return render_template('feed.html', posts=posts, type=type, next=resp.nextPageId)
    
@app.route('/populate')
def populate():
    global stub
    resp = populate_database(stub)
    return 'OK'
    
@app.route('/post/<post_id>')
def post(post_id):
    global stub
    resp = get_post(stub, idstring=post_id, userhandle='')
    return render_template('post.html', post=resp)

@app.route('/')
def hello_world():
    return serveFeed("forum")

@app.route('/forum')
def forum():
    return serveFeed("forum")

@app.route('/news')
def news():
    return serveFeed("news")

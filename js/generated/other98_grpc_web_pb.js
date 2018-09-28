/**
 * @fileoverview gRPC-Web generated client stub for com.fanreact.other98
 * @enhanceable
 * @public
 */

// GENERATED CODE -- DO NOT EDIT!



const grpc = {};
grpc.web = require('grpc-web');

const proto = {};
proto.com = {};
proto.com.fanreact = {};
proto.com.fanreact.other98 = require('./other98_pb.js');

/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.com.fanreact.other98.TheOther98Client =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!grpc.web.GrpcWebClientBase} The client
   */
  this.client_ = new grpc.web.GrpcWebClientBase(options);

  /**
   * @private @const {string} The hostname
   */
  this.hostname_ = hostname;

  /**
   * @private @const {?Object} The credentials to be used to connect
   *    to the server
   */
  this.credentials_ = credentials;

  /**
   * @private @const {?Object} Options for the client
   */
  this.options_ = options;
};


/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.com.fanreact.other98.TheOther98PromiseClient =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!proto.com.fanreact.other98.TheOther98Client} The delegate callback based client
   */
  this.delegateClient_ = new proto.com.fanreact.other98.TheOther98Client(
      hostname, credentials, options);

};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.com.fanreact.other98.FeedRequest,
 *   !proto.com.fanreact.other98.FeedResponseView>}
 */
const methodInfo_GetFeed = new grpc.web.AbstractClientBase.MethodInfo(
  proto.com.fanreact.other98.FeedResponseView,
  /** @param {!proto.com.fanreact.other98.FeedRequest} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.com.fanreact.other98.FeedResponseView.deserializeBinary
);


/**
 * @param {!proto.com.fanreact.other98.FeedRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.com.fanreact.other98.FeedResponseView)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.com.fanreact.other98.FeedResponseView>|undefined}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98Client.prototype.getFeed =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/com.fanreact.other98.TheOther98/GetFeed',
      request,
      metadata,
      methodInfo_GetFeed,
      callback);
};


/**
 * @param {!proto.com.fanreact.other98.FeedRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.com.fanreact.other98.FeedResponseView>}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98PromiseClient.prototype.getFeed =
    function(request, metadata) {
  return new Promise((resolve, reject) => {
    this.delegateClient_.getFeed(
      request, metadata, (error, response) => {
        error ? reject(error) : resolve(response);
      });
  });
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.com.fanreact.other98.GetRequest,
 *   !proto.com.fanreact.other98.PostView>}
 */
const methodInfo_GetPost = new grpc.web.AbstractClientBase.MethodInfo(
  proto.com.fanreact.other98.PostView,
  /** @param {!proto.com.fanreact.other98.GetRequest} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.com.fanreact.other98.PostView.deserializeBinary
);


/**
 * @param {!proto.com.fanreact.other98.GetRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.com.fanreact.other98.PostView)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.com.fanreact.other98.PostView>|undefined}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98Client.prototype.getPost =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/com.fanreact.other98.TheOther98/GetPost',
      request,
      metadata,
      methodInfo_GetPost,
      callback);
};


/**
 * @param {!proto.com.fanreact.other98.GetRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.com.fanreact.other98.PostView>}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98PromiseClient.prototype.getPost =
    function(request, metadata) {
  return new Promise((resolve, reject) => {
    this.delegateClient_.getPost(
      request, metadata, (error, response) => {
        error ? reject(error) : resolve(response);
      });
  });
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.com.fanreact.other98.GetRequest,
 *   !proto.com.fanreact.other98.ProfileResponseView>}
 */
const methodInfo_GetProfile = new grpc.web.AbstractClientBase.MethodInfo(
  proto.com.fanreact.other98.ProfileResponseView,
  /** @param {!proto.com.fanreact.other98.GetRequest} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.com.fanreact.other98.ProfileResponseView.deserializeBinary
);


/**
 * @param {!proto.com.fanreact.other98.GetRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.com.fanreact.other98.ProfileResponseView)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.com.fanreact.other98.ProfileResponseView>|undefined}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98Client.prototype.getProfile =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/com.fanreact.other98.TheOther98/GetProfile',
      request,
      metadata,
      methodInfo_GetProfile,
      callback);
};


/**
 * @param {!proto.com.fanreact.other98.GetRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.com.fanreact.other98.ProfileResponseView>}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98PromiseClient.prototype.getProfile =
    function(request, metadata) {
  return new Promise((resolve, reject) => {
    this.delegateClient_.getProfile(
      request, metadata, (error, response) => {
        error ? reject(error) : resolve(response);
      });
  });
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.com.fanreact.other98.CreatePostRequest,
 *   !proto.com.fanreact.other98.Result>}
 */
const methodInfo_CreatePost = new grpc.web.AbstractClientBase.MethodInfo(
  proto.com.fanreact.other98.Result,
  /** @param {!proto.com.fanreact.other98.CreatePostRequest} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.com.fanreact.other98.Result.deserializeBinary
);


/**
 * @param {!proto.com.fanreact.other98.CreatePostRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.com.fanreact.other98.Result)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.com.fanreact.other98.Result>|undefined}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98Client.prototype.createPost =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/com.fanreact.other98.TheOther98/CreatePost',
      request,
      metadata,
      methodInfo_CreatePost,
      callback);
};


/**
 * @param {!proto.com.fanreact.other98.CreatePostRequest} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.com.fanreact.other98.Result>}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98PromiseClient.prototype.createPost =
    function(request, metadata) {
  return new Promise((resolve, reject) => {
    this.delegateClient_.createPost(
      request, metadata, (error, response) => {
        error ? reject(error) : resolve(response);
      });
  });
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.com.fanreact.other98.Comment,
 *   !proto.com.fanreact.other98.Result>}
 */
const methodInfo_CreateComment = new grpc.web.AbstractClientBase.MethodInfo(
  proto.com.fanreact.other98.Result,
  /** @param {!proto.com.fanreact.other98.Comment} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.com.fanreact.other98.Result.deserializeBinary
);


/**
 * @param {!proto.com.fanreact.other98.Comment} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.com.fanreact.other98.Result)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.com.fanreact.other98.Result>|undefined}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98Client.prototype.createComment =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/com.fanreact.other98.TheOther98/CreateComment',
      request,
      metadata,
      methodInfo_CreateComment,
      callback);
};


/**
 * @param {!proto.com.fanreact.other98.Comment} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.com.fanreact.other98.Result>}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98PromiseClient.prototype.createComment =
    function(request, metadata) {
  return new Promise((resolve, reject) => {
    this.delegateClient_.createComment(
      request, metadata, (error, response) => {
        error ? reject(error) : resolve(response);
      });
  });
};


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.com.fanreact.other98.Void,
 *   !proto.com.fanreact.other98.Void>}
 */
const methodInfo_PopulateDatabase = new grpc.web.AbstractClientBase.MethodInfo(
  proto.com.fanreact.other98.Void,
  /** @param {!proto.com.fanreact.other98.Void} request */
  function(request) {
    return request.serializeBinary();
  },
  proto.com.fanreact.other98.Void.deserializeBinary
);


/**
 * @param {!proto.com.fanreact.other98.Void} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.com.fanreact.other98.Void)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.com.fanreact.other98.Void>|undefined}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98Client.prototype.populateDatabase =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/com.fanreact.other98.TheOther98/PopulateDatabase',
      request,
      metadata,
      methodInfo_PopulateDatabase,
      callback);
};


/**
 * @param {!proto.com.fanreact.other98.Void} request The
 *     request proto
 * @param {!Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.com.fanreact.other98.Void>}
 *     The XHR Node Readable Stream
 */
proto.com.fanreact.other98.TheOther98PromiseClient.prototype.populateDatabase =
    function(request, metadata) {
  return new Promise((resolve, reject) => {
    this.delegateClient_.populateDatabase(
      request, metadata, (error, response) => {
        error ? reject(error) : resolve(response);
      });
  });
};


module.exports = proto.com.fanreact.other98;


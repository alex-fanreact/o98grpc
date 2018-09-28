const {FeedRequest, Void} = require('./generated/other98_pb.js');
const {TheOther98Client} = require('./generated/other98_grpc_web_pb.js');

var o98 = new TheOther98Client('http://104.248.239.78:8080');

var request = new FeedRequest();
request.setPosttagsList(['forum']);
//request.
console.log("test")
var rt = o98.getFeed(request, {}, function(err, response) {
    console.log("feed");
  console.log(err);
  console.log(response);
  if (response == null) {
      return;
  }

  var list = response.getPostfeedviewsList()
  for(i = 0; i < list.length; i++) {
    var elem = list[i];
    var sv = elem.getPostsmallview();
    var title = "<h1> Post title: " + sv.getTitle() + "</h1>\n";
    var descr = "<h2> post description: " + sv.getDescription() + "</h2>\n";
    var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    var date = "<span> Created on " + (new Date(sv.getCreatedate())).toLocaleDateString('en', options) + "</span>\n";
    var author = "<span> Author: " + sv.getAuthorhandle() + "</span>\n";

    var html = title + descr + date + author + "<br/> <br/> <br/>";
    document.body.innerHTML += html;
  }
  
});

/*var rt2 = o98.populateDatabase(new Void, {}, function(err, response){
    console.log(err);
    console.log(response);
});*/
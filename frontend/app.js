var app = angular.module('myApp', ['ngRoute']);
var api_url = "http://35.197.185.226:8000/"

app.config(function($routeProvider) {
  $routeProvider

  .when('/', {
    templateUrl : 'pages/home.html',
    controller  : 'HomeController'
  })

  .when('/blog', {
    templateUrl : 'pages/blog.html',
    controller  : 'BlogController'
  })

  .when('/about', {
    templateUrl : 'pages/about.html',
    controller  : 'AboutController'
  })

  .otherwise({redirectTo: '/'});
});


app.controller('HomeController', function($scope, $http) {

// come back and do a test for going to a different part of the api
  $http.get(api_url)
    .then(function success(response) {
      // $scope.message = 'yay'
      $scope.hostname = response.data.hostname;
      $scope.name = response.data.name;
      $scope.visits = response.data.visits;
    }, function error(response) {
      // $scope.message = 'nay'
      $scope.message = response.data;
    });

});

app.controller('BlogController', function($scope) {
  $scope.message = 'Hello from BlogController';
});

app.controller('AboutController', function($scope) {
  $scope.message = 'Hello from AboutController';
});

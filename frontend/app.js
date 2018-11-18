var app = angular.module('myApp', ['ngRoute']);
var api_url = "http://" + self.location.hostname + ":5000/"


app.config(function($routeProvider) {
  $routeProvider

  .when('/', {
    templateUrl : 'pages/home.html',
    controller  : 'HomeController'
  })

  .when('/ping', {
    templateUrl : 'pages/ping.html',
    controller  : 'PingController'
  })

  .when('/toggleNetwork', {
    templateUrl : 'pages/toggleNetwork.html',
    controller  : 'ToggleNetworkController'
  })

  .otherwise({redirectTo: '/'});
});


app.controller('HomeController', function($scope, $http) {

  $http.get(api_url)
    .then(function success(response) {
      $scope.hostname = self.location.hostname;
      $scope.name = response.data.name;
      $scope.visits = response.data.visits;
    }, function error(response) {
      $scope.message = response.data;
    });

});

app.controller('PingController', function($scope, $http) {

  $http.get(api_url + 'ping')
    .then(function success(response) {
      $scope.answer = response.data;
    }, function error(response) {
      $scope.message = response.data;
    });

});

app.controller('ToggleNetworkController', function($scope, $http) {

  $scope.status = 'unknown';

  $scope.toggleNetwork = function(networkStatus) {
    $http.post(api_url + 'networkOn', networkStatus)
      .then(function success(response) {
        if (response.data.networkOn == 'True')
          $scope.status = 'on';
        else
          $scope.status = 'off';
      }, function error(response) {
        $scope.status = response.data;
      });
  };

});

app.controller('BlogController', function($scope) {
  $scope.message = 'Hello from BlogController';
});

app.controller('AboutController', function($scope) {
  $scope.message = 'Hello from AboutController';
});

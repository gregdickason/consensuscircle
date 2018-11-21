var app = angular.module('myApp', ['ngRoute']);
var api_url = "http://" + self.location.hostname + ":5000/"

app.factory('SharedCore', function($http, $cookies, $location) {
    return {

        changePage: function(location) {
            $location.path(location);
        }

  };
})

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

  .when('/agentConfig', {
    templateUrl : 'pages/agentConfig.html',
    controller  : 'agentConfigController'
  })

  .when('/editAgentConfig', {
    templateUrl : 'pages/editAgentConfig.html',
    controller  : 'editAgentConfigController'
  })

  .when('/instructionPool', {
    templateUrl : 'pages/instructionPool.html',
    controller  : 'instructionPoolController'
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

app.controller('agentConfigController', function($scope, $http) {

    $http.get(api_url + 'getConfig')
      .then(function success(response) {
        $scope.config = response.data;
      }, function error(response) {
        $scope.message = response.data;
      });

});

app.controller('instructionPoolController', function($scope, $http) {

    $http.get(api_url + 'instructionPool')
      .then(function success(response) {
        $scope.pool = response.data;
      }, function error(response) {
        $scope.message = response.data;
      });

});

app.controller('editAgentConfigController', function($scope, $http) {

    $http.get(api_url + 'getConfig')
      .then(function success(response) {
        $scope.config = response.data;
      }, function error(response) {
        $scope.message = response.data;
      });

  $scope.update = '';

  $scope.setConfig = function(config) {
    $http.post(api_url + 'updateConfig', config)
      .then(function success(response) {
          window.location.href = '#!/agentConfig';
      }, function error(response) {
          $scope.update = 'error in updating settings';
      });
  };

});

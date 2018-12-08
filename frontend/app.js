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

  .when('/entities', {
    templateUrl : 'pages/entities.html',
    controller  : 'entityController'
  })

  .when('/attribute', {
      templateUrl : 'pages/attribute.html',
      controller  : 'attributeController'
  })


  .when('/genesisBlock', {
    templateUrl : 'pages/genesisBlock.html',
    controller  : 'genesisBlockController'
  })

  .when('/publishBlock', {
    templateUrl : 'pages/publishBlock.html',
    controller  : 'publishBlockController'
  })

  .when('/latestBlock', {
    templateUrl : 'pages/block.html',
    controller  : 'blockController'
  })

  .when('/newInstruction', {
    templateUrl : 'pages/instruction.html',
    controller  : 'newInstructionController'
  })

  .when('/executeInstruction', {
    templateUrl : 'pages/executeInstruction.html',
    controller  : 'executeInstructionController'
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

app.controller('genesisBlockController', function($scope, $http) {

  $http.get(api_url + 'genesisBlock')
    .then(function success(response) {
      $scope.block = response.data;
    }, function error(response) {
      $scope.message = response.data;
    });

});

app.controller('blockController', function($scope, $http) {

  $http.get(api_url + 'block')
    .then(function success(response) {
      $scope.block = response.data;
    }, function error(response) {
      $scope.message = response.data;
    });

});

app.controller('ToggleNetworkController', function($scope, $http) {

  $http.get(api_url + 'getNetworkStatus')
    .then(function success(response) {
      $scope.status = response.data.network
    }, function error(response) {
      $scope.message = response.data;
    });

  $scope.toggleNetwork = function(networkStatus) {
    $http.post(api_url + 'setNetworkStatus', networkStatus)
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


app.controller('entityController', function($scope, $http) {

    $http.get(api_url + 'getEntities')
      .then(function success(response) {
        $scope.entities = response.data;
      }, function error(response) {
        $scope.message = response.data;
      });

  $scope.update = '';

  $scope.chooseEntity = function(chosen) {
    $http.post(api_url + 'entity', chosen)
      .then(function success(response) {
          $scope.entityDetails = response.data;
      }, function error(response) {
          $scope.update = 'error in getting entity';
      });
  };

});

app.controller('attributeController', function($scope, $http) {

    $http.get(api_url + 'attribute')
      .then(function success(response) {
        $scope.attribute = response.data;
      }, function error(response) {
        $scope.message = response.data;
      });

  $scope.update = '';

  $scope.chooseAttribute = function(chosen) {
    $http.post(api_url + 'entity', chosen)
      .then(function success(response) {
          $scope.entityDetails = response.data;
      }, function error(response) {
          $scope.update = 'error in getting entity';
      });
  };

});

app.controller('publishBlockController', function($scope, $http) {

  $scope.blockToPublish = function(chosen) {
    $http.post(api_url + 'publishBlock', chosen)
      .then(function success(response) {
          $scope.result = response.data;
      }, function error(response) {
          $scope.update = 'error in getting entity';
      });
  };

});


app.controller('newInstructionController', function($scope, $http) {

  //need to add hashing and Signing
  $scope.instruction = {};
  $scope.instruction.instruction = {};
  $scope.started = false;
  $scope.instruction.instruction.args = [];
  $scope.instruction.instruction.keys = [];
  $scope.instruction.instructionHash = "";
  $scope.instruction.signature = "";
  $scope.instruction.instruction.sender = "5ad77a2a5b591824805a5d3dac653f5a54af47ca6b8161883c1c17972b90938c";

  $http.get(api_url + 'getInstructionNames')
    .then(function success(response) {
      $scope.instructionTypes = response.data;
    }, function error(response) {
      $scope.message = response.data;
    });



   $scope.getInstructionTypeRequirements = function(name) {
     $scope.started = true;

     $http.post(api_url + 'getLuaHash', name)
       .then(function success(response) {
           $scope.luaHash = response.data;
           $scope.instruction.instruction.luaHash = $scope.luaHash;
       }, function error(response) {
           $scope.update = 'error in getting entity';
       });

       $http.post(api_url + 'getInstructionArguments', name)
         .then(function success(response) {
             $scope.argumentList = response.data;
         }, function error(response) {
             $scope.update = 'error in getting entity';
         });

         $http.post(api_url + 'getInstructionKeys', name)
           .then(function success(response) {
               $scope.keyList = response.data;
           }, function error(response) {
               $scope.update = 'error in getting entity';
           });
   }

   $scope.addFormField = function() {
       $scope.table.fields.push('');
     }

  $scope.addInstruction = function(instruction) {
    instructionNoWhiteSpace = JSON.stringify(instruction.instruction)

    temp1 = instructionNoWhiteSpace.replace(/\s/g,'')
    temp2 = temp1.replace(/\"/g,'\'')

    var shaObj = new jsSHA("SHA-256", "TEXT");
    shaObj.update(temp2);
    var hash = shaObj.getHash("HEX");

    instruction.instructionHash = hash;

    $http.post(api_url + 'addInstruction', instruction)
      .then(function success(response) {
          $scope.result = response.data;
      }, function error(response) {
          $scope.update = 'error in getting entity';
      });
  };


});

app.controller('executeInstructionController', function($scope, $http) {

    $http.get(api_url + 'getPendingInstructions')
      .then(function success(response) {
        $scope.instructions = response.data;
      }, function error(response) {
        $scope.message = response.data;
      });

  $scope.executeInstruction = function(chosen) {
    $http.post(api_url + 'executeInstruction', chosen)
      .then(function success(response) {
          $scope.reponse = response.data;
      }, function error(response) {
          $scope.response = 'error in executing instruction';
      });
  };

});

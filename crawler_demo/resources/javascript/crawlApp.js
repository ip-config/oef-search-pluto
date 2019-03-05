angular.module('crawlApp', []).controller('crawlController', [ '$location', '$scope', '$http', '$interval', '$timeout', function ($location, $scope, $http, $interval, $timeout) {

    $scope.g = null;

    function RemoveLastDirectoryPartOf(the_url, removals)
    {
        var the_arr = the_url.split('/');
        var i;
        for (i = 0; i < removals; i++) {
            the_arr.pop();
        }
        return( the_arr.join('/') );
    }

    $scope.svg_url = "/svg";

    $scope.gather_network_data = new CrawlerDisplay($http, $scope.svg_url, "map");

    $scope.load = function() {
        console.log("TICK");
        $scope.gather_network_data.tick();
    }

    $scope.init = function() {
        $scope.load();
        $interval( $scope.load, 200);
    }

    $scope.clearData = function() {
        if ($scope.g_blobs)
        {
            $scope.g_blobs.addData(
                {
                    nodes: [],
                    links: [],
                }
            );
        }
    }

    $scope.init();

}]).config(function ($locationProvider) {
    $locationProvider.html5Mode(true);
})

if (typeof kotlin === 'undefined') {
  throw new Error("Error loading module 'website'. Its dependency 'kotlin' was not found. Please, check whether 'kotlin' is loaded prior to 'website'.");
}
var website = function (_, Kotlin) {
  'use strict';
  var Kind_INTERFACE = Kotlin.Kind.INTERFACE;
  var throwCCE = Kotlin.throwCCE;
  var addClass = Kotlin.kotlin.dom.addClass_hhb33f$;
  var Unit = Kotlin.kotlin.Unit;
  var Kind_CLASS = Kotlin.Kind.CLASS;
  var toShort = Kotlin.toShort;
  var print = Kotlin.kotlin.io.print_s8jyv4$;
  function SearchEventHandler() {
  }
  SearchEventHandler.$metadata$ = {
    kind: Kind_INTERFACE,
    simpleName: 'SearchEventHandler',
    interfaces: []
  };
  function MainSearchSite(containerId, title, searchEvent) {
    this.searchEvent_0 = searchEvent;
    var tmp$, tmp$_0, tmp$_1, tmp$_2;
    this.container_0 = Kotlin.isType(tmp$ = document.getElementById(containerId), HTMLDivElement) ? tmp$ : throwCCE();
    var $receiver = document.createElement('h1');
    $receiver.innerHTML = title;
    addClass($receiver, ['title']);
    this.title_0 = $receiver;
    var $receiver_0 = Kotlin.isType(tmp$_0 = document.createElement('input'), HTMLInputElement) ? tmp$_0 : throwCCE();
    addClass($receiver_0, ['search_box']);
    $receiver_0.id = 'search_box';
    $receiver_0.addEventListener('keypress', MainSearchSite$searchBox$lambda$lambda(this, $receiver_0));
    this.searchBox_0 = $receiver_0;
    var $receiver_1 = Kotlin.isType(tmp$_1 = document.createElement('button'), HTMLButtonElement) ? tmp$_1 : throwCCE();
    addClass($receiver_1, ['search_button']);
    $receiver_1.textContent = 'Search';
    $receiver_1.addEventListener('click', MainSearchSite$searchButton$lambda$lambda(this));
    this.searchButton_0 = $receiver_1;
    var $receiver_2 = Kotlin.isType(tmp$_2 = document.createElement('div'), HTMLDivElement) ? tmp$_2 : throwCCE();
    addClass($receiver_2, ['search_div']);
    $receiver_2.append(this.searchBox_0, this.searchButton_0);
    this.search_0 = $receiver_2;
  }
  MainSearchSite.prototype.assemble = function () {
    this.container_0.append(this.title_0, this.search_0);
  };
  function MainSearchSite$searchBox$lambda$lambda(this$MainSearchSite, this$) {
    return function (it) {
      var tmp$;
      Kotlin.isType(tmp$ = it, KeyboardEvent) ? tmp$ : throwCCE();
      if (it.keyCode === 13) {
        this$MainSearchSite.searchEvent_0.onSearch_61zpoe$(this$.value);
      }
      return Unit;
    };
  }
  function MainSearchSite$searchButton$lambda$lambda(this$MainSearchSite) {
    return function (it) {
      this$MainSearchSite.searchEvent_0.onSearch_61zpoe$(this$MainSearchSite.searchBox_0.value);
      return Unit;
    };
  }
  MainSearchSite.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'MainSearchSite',
    interfaces: []
  };
  function NetworkCom(search_uri) {
    this.search_uri_0 = search_uri;
  }
  function NetworkCom$onSearch$lambda(closure$xmlHttp) {
    return function (it) {
      var tmp$;
      if (closure$xmlHttp.v.readyState === toShort(4) && closure$xmlHttp.v.status === toShort(200)) {
        var txt = closure$xmlHttp.v.responseText;
        print(txt);
        var resp = document.createElement('p');
        resp.innerHTML = txt;
        (tmp$ = document.getElementById('container')) != null ? tmp$.appendChild(resp) : null;
      }
      return Unit;
    };
  }
  NetworkCom.prototype.onSearch_61zpoe$ = function (text) {
    var xmlHttp = {v: new XMLHttpRequest()};
    xmlHttp.v.withCredentials = true;
    xmlHttp.v.open('POST', this.search_uri_0, true);
    xmlHttp.v.setRequestHeader('Content-Type', 'application/json');
    xmlHttp.v.setRequestHeader('Accept', 'application/json');
    xmlHttp.v.onload = NetworkCom$onSearch$lambda(xmlHttp);
    var body = '{' + '"ttl":3,' + '"model":' + '{' + '"' + 'description' + '"' + ': ' + '"' + text + '"' + '}' + '}';
    xmlHttp.v.send(body);
  };
  NetworkCom.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'NetworkCom',
    interfaces: [SearchEventHandler]
  };
  function main(args) {
    var networkCom = new NetworkCom('https://localhost:7500/json/search');
    var mainPage = new MainSearchSite('container', 'OEF Search', networkCom);
    mainPage.assemble();
  }
  _.SearchEventHandler = SearchEventHandler;
  _.MainSearchSite = MainSearchSite;
  _.NetworkCom = NetworkCom;
  _.main_kand9s$ = main;
  main([]);
  Kotlin.defineModule('website', _);
  return _;
}(typeof website === 'undefined' ? {} : website, kotlin);

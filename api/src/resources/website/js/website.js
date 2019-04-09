if (typeof kotlin === 'undefined') {
  throw new Error("Error loading module 'website'. Its dependency 'kotlin' was not found. Please, check whether 'kotlin' is loaded prior to 'website'.");
}
if (typeof this['kotlinx-serialization-runtime-js'] === 'undefined') {
  throw new Error("Error loading module 'website'. Its dependency 'kotlinx-serialization-runtime-js' was not found. Please, check whether 'kotlinx-serialization-runtime-js' is loaded prior to 'website'.");
}
var website = function (_, Kotlin, $module$kotlinx_serialization_runtime_js) {
  'use strict';
  var Kind_INTERFACE = Kotlin.Kind.INTERFACE;
  var throwCCE = Kotlin.throwCCE;
  var addClass = Kotlin.kotlin.dom.addClass_hhb33f$;
  var Unit = Kotlin.kotlin.Unit;
  var equals = Kotlin.equals;
  var Kind_CLASS = Kotlin.Kind.CLASS;
  var Kind_OBJECT = Kotlin.Kind.OBJECT;
  var SerialClassDescImpl = $module$kotlinx_serialization_runtime_js.kotlinx.serialization.internal.SerialClassDescImpl;
  var UnknownFieldException = $module$kotlinx_serialization_runtime_js.kotlinx.serialization.UnknownFieldException;
  var internal = $module$kotlinx_serialization_runtime_js.kotlinx.serialization.internal;
  var GeneratedSerializer = $module$kotlinx_serialization_runtime_js.kotlinx.serialization.internal.GeneratedSerializer;
  var MissingFieldException = $module$kotlinx_serialization_runtime_js.kotlinx.serialization.MissingFieldException;
  var toShort = Kotlin.toShort;
  var print = Kotlin.kotlin.io.print_s8jyv4$;
  var toDouble = Kotlin.kotlin.text.toDouble_pdl1vz$;
  var Json = $module$kotlinx_serialization_runtime_js.kotlinx.serialization.json.Json;
  function SearchEventHandler() {
  }
  SearchEventHandler.$metadata$ = {
    kind: Kind_INTERFACE,
    simpleName: 'SearchEventHandler',
    interfaces: []
  };
  function MainSearchSite(containerId, title, searchEvent) {
    this.searchEvent_0 = searchEvent;
    var tmp$, tmp$_0, tmp$_1, tmp$_2, tmp$_3, tmp$_4, tmp$_5;
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
    var $receiver_2 = Kotlin.isType(tmp$_2 = document.createElement('input'), HTMLInputElement) ? tmp$_2 : throwCCE();
    addClass($receiver_2, ['location_div_input']);
    $receiver_2.value = 'LON';
    $receiver_2.addEventListener('click', MainSearchSite$lon_input$lambda$lambda($receiver_2));
    $receiver_2.addEventListener('onfocusout', MainSearchSite$lon_input$lambda$lambda_0($receiver_2));
    this.lon_input_0 = $receiver_2;
    var $receiver_3 = Kotlin.isType(tmp$_3 = document.createElement('input'), HTMLInputElement) ? tmp$_3 : throwCCE();
    addClass($receiver_3, ['location_div_input']);
    $receiver_3.value = 'LAT';
    $receiver_3.addEventListener('click', MainSearchSite$lat_input$lambda$lambda($receiver_3));
    $receiver_3.addEventListener('onfocusout', MainSearchSite$lat_input$lambda$lambda_0($receiver_3));
    this.lat_input_0 = $receiver_3;
    var $receiver_4 = Kotlin.isType(tmp$_4 = document.createElement('div'), HTMLDivElement) ? tmp$_4 : throwCCE();
    addClass($receiver_4, ['location_div']);
    $receiver_4.append(this.lon_input_0, this.lat_input_0);
    this.locationBox_0 = $receiver_4;
    var $receiver_5 = Kotlin.isType(tmp$_5 = document.createElement('div'), HTMLDivElement) ? tmp$_5 : throwCCE();
    addClass($receiver_5, ['search_div']);
    $receiver_5.append(this.searchBox_0, this.locationBox_0, this.searchButton_0);
    this.search_0 = $receiver_5;
  }
  MainSearchSite.prototype.assemble = function () {
    this.container_0.append(this.title_0, this.search_0);
  };
  function MainSearchSite$searchBox$lambda$lambda(this$MainSearchSite, this$) {
    return function (it) {
      var tmp$;
      Kotlin.isType(tmp$ = it, KeyboardEvent) ? tmp$ : throwCCE();
      if (it.keyCode === 13) {
        this$MainSearchSite.searchEvent_0.onSearch_6hosri$(this$.value, this$MainSearchSite.lon_input_0.value, this$MainSearchSite.lat_input_0.value);
      }
      return Unit;
    };
  }
  function MainSearchSite$searchButton$lambda$lambda(this$MainSearchSite) {
    return function (it) {
      this$MainSearchSite.searchEvent_0.onSearch_6hosri$(this$MainSearchSite.searchBox_0.value, this$MainSearchSite.lon_input_0.value, this$MainSearchSite.lat_input_0.value);
      return Unit;
    };
  }
  function MainSearchSite$lon_input$lambda$lambda(this$) {
    return function (it) {
      if (equals(this$.value, 'LON')) {
        this$.value = '';
      }
      return Unit;
    };
  }
  function MainSearchSite$lon_input$lambda$lambda_0(this$) {
    return function (it) {
      if (this$.value.length === 0) {
        this$.value = 'LON';
      }
      return Unit;
    };
  }
  function MainSearchSite$lat_input$lambda$lambda(this$) {
    return function (it) {
      if (equals(this$.value, 'LAT')) {
        this$.value = '';
      }
      return Unit;
    };
  }
  function MainSearchSite$lat_input$lambda$lambda_0(this$) {
    return function (it) {
      if (this$.value.length === 0) {
        this$.value = 'LAT';
      }
      return Unit;
    };
  }
  MainSearchSite.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'MainSearchSite',
    interfaces: []
  };
  function DirectedSearch(target) {
    DirectedSearch$Companion_getInstance();
    if (target === void 0)
      target = new DirectedSearch$PlaneTarget();
    this.target = target;
  }
  function DirectedSearch$PlaneTarget(geo) {
    DirectedSearch$PlaneTarget$Companion_getInstance();
    if (geo === void 0)
      geo = new DirectedSearch$PlaneTarget$GeoLocation();
    this.geo = geo;
  }
  function DirectedSearch$PlaneTarget$GeoLocation(lon, lat) {
    DirectedSearch$PlaneTarget$GeoLocation$Companion_getInstance();
    if (lon === void 0)
      lon = 0.0;
    if (lat === void 0)
      lat = 0.0;
    this.lon = lon;
    this.lat = lat;
  }
  function DirectedSearch$PlaneTarget$GeoLocation$Companion() {
    DirectedSearch$PlaneTarget$GeoLocation$Companion_instance = this;
  }
  DirectedSearch$PlaneTarget$GeoLocation$Companion.prototype.serializer = function () {
    return DirectedSearch$PlaneTarget$GeoLocation$$serializer_getInstance();
  };
  DirectedSearch$PlaneTarget$GeoLocation$Companion.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: 'Companion',
    interfaces: []
  };
  var DirectedSearch$PlaneTarget$GeoLocation$Companion_instance = null;
  function DirectedSearch$PlaneTarget$GeoLocation$Companion_getInstance() {
    if (DirectedSearch$PlaneTarget$GeoLocation$Companion_instance === null) {
      new DirectedSearch$PlaneTarget$GeoLocation$Companion();
    }
    return DirectedSearch$PlaneTarget$GeoLocation$Companion_instance;
  }
  function DirectedSearch$PlaneTarget$GeoLocation$$serializer() {
    this.descriptor_zfewtw$_0 = new SerialClassDescImpl('DirectedSearch.PlaneTarget.GeoLocation', this);
    this.descriptor.addElement_ivxn3r$('lon', false);
    this.descriptor.addElement_ivxn3r$('lat', false);
    DirectedSearch$PlaneTarget$GeoLocation$$serializer_instance = this;
  }
  Object.defineProperty(DirectedSearch$PlaneTarget$GeoLocation$$serializer.prototype, 'descriptor', {
    get: function () {
      return this.descriptor_zfewtw$_0;
    }
  });
  DirectedSearch$PlaneTarget$GeoLocation$$serializer.prototype.serialize_awe97i$ = function (encoder, obj) {
    var output = encoder.beginStructure_r0sa6z$(this.descriptor, []);
    output.encodeDoubleElement_imzr5k$(this.descriptor, 0, obj.lon);
    output.encodeDoubleElement_imzr5k$(this.descriptor, 1, obj.lat);
    output.endStructure_qatsm0$(this.descriptor);
  };
  DirectedSearch$PlaneTarget$GeoLocation$$serializer.prototype.deserialize_nts5qn$ = function (decoder) {
    var index, readAll = false;
    var bitMask0 = 0;
    var local0
    , local1;
    var input = decoder.beginStructure_r0sa6z$(this.descriptor, []);
    loopLabel: while (true) {
      index = input.decodeElementIndex_qatsm0$(this.descriptor);
      switch (index) {
        case -2:
          readAll = true;
        case 0:
          local0 = input.decodeDoubleElement_3zr2iy$(this.descriptor, 0);
          bitMask0 |= 1;
          if (!readAll)
            break;
        case 1:
          local1 = input.decodeDoubleElement_3zr2iy$(this.descriptor, 1);
          bitMask0 |= 2;
          if (!readAll)
            break;
        case -1:
          break loopLabel;
        default:throw new UnknownFieldException(index);
      }
    }
    input.endStructure_qatsm0$(this.descriptor);
    return DirectedSearch$PlaneTarget$DirectedSearch$PlaneTarget$GeoLocation_init(bitMask0, local0, local1, null);
  };
  DirectedSearch$PlaneTarget$GeoLocation$$serializer.prototype.childSerializers = function () {
    return [internal.DoubleSerializer, internal.DoubleSerializer];
  };
  DirectedSearch$PlaneTarget$GeoLocation$$serializer.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: '$serializer',
    interfaces: [GeneratedSerializer]
  };
  var DirectedSearch$PlaneTarget$GeoLocation$$serializer_instance = null;
  function DirectedSearch$PlaneTarget$GeoLocation$$serializer_getInstance() {
    if (DirectedSearch$PlaneTarget$GeoLocation$$serializer_instance === null) {
      new DirectedSearch$PlaneTarget$GeoLocation$$serializer();
    }
    return DirectedSearch$PlaneTarget$GeoLocation$$serializer_instance;
  }
  function DirectedSearch$PlaneTarget$DirectedSearch$PlaneTarget$GeoLocation_init(seen, lon, lat, serializationConstructorMarker) {
    var $this = Object.create(DirectedSearch$PlaneTarget$GeoLocation.prototype);
    if ((seen & 1) === 0)
      throw new MissingFieldException('lon');
    else
      $this.lon = lon;
    if ((seen & 2) === 0)
      throw new MissingFieldException('lat');
    else
      $this.lat = lat;
    return $this;
  }
  DirectedSearch$PlaneTarget$GeoLocation.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'GeoLocation',
    interfaces: []
  };
  DirectedSearch$PlaneTarget$GeoLocation.prototype.component1 = function () {
    return this.lon;
  };
  DirectedSearch$PlaneTarget$GeoLocation.prototype.component2 = function () {
    return this.lat;
  };
  DirectedSearch$PlaneTarget$GeoLocation.prototype.copy_lu1900$ = function (lon, lat) {
    return new DirectedSearch$PlaneTarget$GeoLocation(lon === void 0 ? this.lon : lon, lat === void 0 ? this.lat : lat);
  };
  DirectedSearch$PlaneTarget$GeoLocation.prototype.toString = function () {
    return 'GeoLocation(lon=' + Kotlin.toString(this.lon) + (', lat=' + Kotlin.toString(this.lat)) + ')';
  };
  DirectedSearch$PlaneTarget$GeoLocation.prototype.hashCode = function () {
    var result = 0;
    result = result * 31 + Kotlin.hashCode(this.lon) | 0;
    result = result * 31 + Kotlin.hashCode(this.lat) | 0;
    return result;
  };
  DirectedSearch$PlaneTarget$GeoLocation.prototype.equals = function (other) {
    return this === other || (other !== null && (typeof other === 'object' && (Object.getPrototypeOf(this) === Object.getPrototypeOf(other) && (Kotlin.equals(this.lon, other.lon) && Kotlin.equals(this.lat, other.lat)))));
  };
  function DirectedSearch$PlaneTarget$Companion() {
    DirectedSearch$PlaneTarget$Companion_instance = this;
  }
  DirectedSearch$PlaneTarget$Companion.prototype.serializer = function () {
    return DirectedSearch$PlaneTarget$$serializer_getInstance();
  };
  DirectedSearch$PlaneTarget$Companion.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: 'Companion',
    interfaces: []
  };
  var DirectedSearch$PlaneTarget$Companion_instance = null;
  function DirectedSearch$PlaneTarget$Companion_getInstance() {
    if (DirectedSearch$PlaneTarget$Companion_instance === null) {
      new DirectedSearch$PlaneTarget$Companion();
    }
    return DirectedSearch$PlaneTarget$Companion_instance;
  }
  function DirectedSearch$PlaneTarget$$serializer() {
    this.descriptor_dsx60k$_0 = new SerialClassDescImpl('DirectedSearch.PlaneTarget', this);
    this.descriptor.addElement_ivxn3r$('geo', false);
    DirectedSearch$PlaneTarget$$serializer_instance = this;
  }
  Object.defineProperty(DirectedSearch$PlaneTarget$$serializer.prototype, 'descriptor', {
    get: function () {
      return this.descriptor_dsx60k$_0;
    }
  });
  DirectedSearch$PlaneTarget$$serializer.prototype.serialize_awe97i$ = function (encoder, obj) {
    var output = encoder.beginStructure_r0sa6z$(this.descriptor, []);
    output.encodeSerializableElement_blecud$(this.descriptor, 0, DirectedSearch$PlaneTarget$GeoLocation$$serializer_getInstance(), obj.geo);
    output.endStructure_qatsm0$(this.descriptor);
  };
  DirectedSearch$PlaneTarget$$serializer.prototype.deserialize_nts5qn$ = function (decoder) {
    var index, readAll = false;
    var bitMask0 = 0;
    var local0;
    var input = decoder.beginStructure_r0sa6z$(this.descriptor, []);
    loopLabel: while (true) {
      index = input.decodeElementIndex_qatsm0$(this.descriptor);
      switch (index) {
        case -2:
          readAll = true;
        case 0:
          local0 = (bitMask0 & 1) === 0 ? input.decodeSerializableElement_s44l7r$(this.descriptor, 0, DirectedSearch$PlaneTarget$GeoLocation$$serializer_getInstance()) : input.updateSerializableElement_ehubvl$(this.descriptor, 0, DirectedSearch$PlaneTarget$GeoLocation$$serializer_getInstance(), local0);
          bitMask0 |= 1;
          if (!readAll)
            break;
        case -1:
          break loopLabel;
        default:throw new UnknownFieldException(index);
      }
    }
    input.endStructure_qatsm0$(this.descriptor);
    return DirectedSearch$DirectedSearch$PlaneTarget_init(bitMask0, local0, null);
  };
  DirectedSearch$PlaneTarget$$serializer.prototype.childSerializers = function () {
    return [DirectedSearch$PlaneTarget$GeoLocation$$serializer_getInstance()];
  };
  DirectedSearch$PlaneTarget$$serializer.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: '$serializer',
    interfaces: [GeneratedSerializer]
  };
  var DirectedSearch$PlaneTarget$$serializer_instance = null;
  function DirectedSearch$PlaneTarget$$serializer_getInstance() {
    if (DirectedSearch$PlaneTarget$$serializer_instance === null) {
      new DirectedSearch$PlaneTarget$$serializer();
    }
    return DirectedSearch$PlaneTarget$$serializer_instance;
  }
  function DirectedSearch$DirectedSearch$PlaneTarget_init(seen, geo, serializationConstructorMarker) {
    var $this = Object.create(DirectedSearch$PlaneTarget.prototype);
    if ((seen & 1) === 0)
      throw new MissingFieldException('geo');
    else
      $this.geo = geo;
    return $this;
  }
  DirectedSearch$PlaneTarget.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'PlaneTarget',
    interfaces: []
  };
  DirectedSearch$PlaneTarget.prototype.component1 = function () {
    return this.geo;
  };
  DirectedSearch$PlaneTarget.prototype.copy_bk5hrt$ = function (geo) {
    return new DirectedSearch$PlaneTarget(geo === void 0 ? this.geo : geo);
  };
  DirectedSearch$PlaneTarget.prototype.toString = function () {
    return 'PlaneTarget(geo=' + Kotlin.toString(this.geo) + ')';
  };
  DirectedSearch$PlaneTarget.prototype.hashCode = function () {
    var result = 0;
    result = result * 31 + Kotlin.hashCode(this.geo) | 0;
    return result;
  };
  DirectedSearch$PlaneTarget.prototype.equals = function (other) {
    return this === other || (other !== null && (typeof other === 'object' && (Object.getPrototypeOf(this) === Object.getPrototypeOf(other) && Kotlin.equals(this.geo, other.geo))));
  };
  function DirectedSearch$Companion() {
    DirectedSearch$Companion_instance = this;
  }
  DirectedSearch$Companion.prototype.serializer = function () {
    return DirectedSearch$$serializer_getInstance();
  };
  DirectedSearch$Companion.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: 'Companion',
    interfaces: []
  };
  var DirectedSearch$Companion_instance = null;
  function DirectedSearch$Companion_getInstance() {
    if (DirectedSearch$Companion_instance === null) {
      new DirectedSearch$Companion();
    }
    return DirectedSearch$Companion_instance;
  }
  function DirectedSearch$$serializer() {
    this.descriptor_l1qx85$_0 = new SerialClassDescImpl('DirectedSearch', this);
    this.descriptor.addElement_ivxn3r$('target', false);
    DirectedSearch$$serializer_instance = this;
  }
  Object.defineProperty(DirectedSearch$$serializer.prototype, 'descriptor', {
    get: function () {
      return this.descriptor_l1qx85$_0;
    }
  });
  DirectedSearch$$serializer.prototype.serialize_awe97i$ = function (encoder, obj) {
    var output = encoder.beginStructure_r0sa6z$(this.descriptor, []);
    output.encodeSerializableElement_blecud$(this.descriptor, 0, DirectedSearch$PlaneTarget$$serializer_getInstance(), obj.target);
    output.endStructure_qatsm0$(this.descriptor);
  };
  DirectedSearch$$serializer.prototype.deserialize_nts5qn$ = function (decoder) {
    var index, readAll = false;
    var bitMask0 = 0;
    var local0;
    var input = decoder.beginStructure_r0sa6z$(this.descriptor, []);
    loopLabel: while (true) {
      index = input.decodeElementIndex_qatsm0$(this.descriptor);
      switch (index) {
        case -2:
          readAll = true;
        case 0:
          local0 = (bitMask0 & 1) === 0 ? input.decodeSerializableElement_s44l7r$(this.descriptor, 0, DirectedSearch$PlaneTarget$$serializer_getInstance()) : input.updateSerializableElement_ehubvl$(this.descriptor, 0, DirectedSearch$PlaneTarget$$serializer_getInstance(), local0);
          bitMask0 |= 1;
          if (!readAll)
            break;
        case -1:
          break loopLabel;
        default:throw new UnknownFieldException(index);
      }
    }
    input.endStructure_qatsm0$(this.descriptor);
    return DirectedSearch_init(bitMask0, local0, null);
  };
  DirectedSearch$$serializer.prototype.childSerializers = function () {
    return [DirectedSearch$PlaneTarget$$serializer_getInstance()];
  };
  DirectedSearch$$serializer.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: '$serializer',
    interfaces: [GeneratedSerializer]
  };
  var DirectedSearch$$serializer_instance = null;
  function DirectedSearch$$serializer_getInstance() {
    if (DirectedSearch$$serializer_instance === null) {
      new DirectedSearch$$serializer();
    }
    return DirectedSearch$$serializer_instance;
  }
  function DirectedSearch_init(seen, target, serializationConstructorMarker) {
    var $this = Object.create(DirectedSearch.prototype);
    if ((seen & 1) === 0)
      throw new MissingFieldException('target');
    else
      $this.target = target;
    return $this;
  }
  DirectedSearch.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'DirectedSearch',
    interfaces: []
  };
  DirectedSearch.prototype.component1 = function () {
    return this.target;
  };
  DirectedSearch.prototype.copy_cki69b$ = function (target) {
    return new DirectedSearch(target === void 0 ? this.target : target);
  };
  DirectedSearch.prototype.toString = function () {
    return 'DirectedSearch(target=' + Kotlin.toString(this.target) + ')';
  };
  DirectedSearch.prototype.hashCode = function () {
    var result = 0;
    result = result * 31 + Kotlin.hashCode(this.target) | 0;
    return result;
  };
  DirectedSearch.prototype.equals = function (other) {
    return this === other || (other !== null && (typeof other === 'object' && (Object.getPrototypeOf(this) === Object.getPrototypeOf(other) && Kotlin.equals(this.target, other.target))));
  };
  function QueryModel(description) {
    QueryModel$Companion_getInstance();
    this.description = description;
  }
  function QueryModel$Companion() {
    QueryModel$Companion_instance = this;
  }
  QueryModel$Companion.prototype.serializer = function () {
    return QueryModel$$serializer_getInstance();
  };
  QueryModel$Companion.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: 'Companion',
    interfaces: []
  };
  var QueryModel$Companion_instance = null;
  function QueryModel$Companion_getInstance() {
    if (QueryModel$Companion_instance === null) {
      new QueryModel$Companion();
    }
    return QueryModel$Companion_instance;
  }
  function QueryModel$$serializer() {
    this.descriptor_jvqjve$_0 = new SerialClassDescImpl('QueryModel', this);
    this.descriptor.addElement_ivxn3r$('description', false);
    QueryModel$$serializer_instance = this;
  }
  Object.defineProperty(QueryModel$$serializer.prototype, 'descriptor', {
    get: function () {
      return this.descriptor_jvqjve$_0;
    }
  });
  QueryModel$$serializer.prototype.serialize_awe97i$ = function (encoder, obj) {
    var output = encoder.beginStructure_r0sa6z$(this.descriptor, []);
    output.encodeStringElement_bgm7zs$(this.descriptor, 0, obj.description);
    output.endStructure_qatsm0$(this.descriptor);
  };
  QueryModel$$serializer.prototype.deserialize_nts5qn$ = function (decoder) {
    var index, readAll = false;
    var bitMask0 = 0;
    var local0;
    var input = decoder.beginStructure_r0sa6z$(this.descriptor, []);
    loopLabel: while (true) {
      index = input.decodeElementIndex_qatsm0$(this.descriptor);
      switch (index) {
        case -2:
          readAll = true;
        case 0:
          local0 = input.decodeStringElement_3zr2iy$(this.descriptor, 0);
          bitMask0 |= 1;
          if (!readAll)
            break;
        case -1:
          break loopLabel;
        default:throw new UnknownFieldException(index);
      }
    }
    input.endStructure_qatsm0$(this.descriptor);
    return QueryModel_init(bitMask0, local0, null);
  };
  QueryModel$$serializer.prototype.childSerializers = function () {
    return [internal.StringSerializer];
  };
  QueryModel$$serializer.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: '$serializer',
    interfaces: [GeneratedSerializer]
  };
  var QueryModel$$serializer_instance = null;
  function QueryModel$$serializer_getInstance() {
    if (QueryModel$$serializer_instance === null) {
      new QueryModel$$serializer();
    }
    return QueryModel$$serializer_instance;
  }
  function QueryModel_init(seen, description, serializationConstructorMarker) {
    var $this = Object.create(QueryModel.prototype);
    if ((seen & 1) === 0)
      throw new MissingFieldException('description');
    else
      $this.description = description;
    return $this;
  }
  QueryModel.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'QueryModel',
    interfaces: []
  };
  QueryModel.prototype.component1 = function () {
    return this.description;
  };
  QueryModel.prototype.copy_61zpoe$ = function (description) {
    return new QueryModel(description === void 0 ? this.description : description);
  };
  QueryModel.prototype.toString = function () {
    return 'QueryModel(description=' + Kotlin.toString(this.description) + ')';
  };
  QueryModel.prototype.hashCode = function () {
    var result = 0;
    result = result * 31 + Kotlin.hashCode(this.description) | 0;
    return result;
  };
  QueryModel.prototype.equals = function (other) {
    return this === other || (other !== null && (typeof other === 'object' && (Object.getPrototypeOf(this) === Object.getPrototypeOf(other) && Kotlin.equals(this.description, other.description))));
  };
  function Query(ttl, model, directed_search) {
    Query$Companion_getInstance();
    if (directed_search === void 0)
      directed_search = new DirectedSearch();
    this.ttl = ttl;
    this.model = model;
    this.directed_search = directed_search;
  }
  function Query$Companion() {
    Query$Companion_instance = this;
  }
  Query$Companion.prototype.serializer = function () {
    return Query$$serializer_getInstance();
  };
  Query$Companion.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: 'Companion',
    interfaces: []
  };
  var Query$Companion_instance = null;
  function Query$Companion_getInstance() {
    if (Query$Companion_instance === null) {
      new Query$Companion();
    }
    return Query$Companion_instance;
  }
  function Query$$serializer() {
    this.descriptor_ce3nwz$_0 = new SerialClassDescImpl('Query', this);
    this.descriptor.addElement_ivxn3r$('ttl', false);
    this.descriptor.addElement_ivxn3r$('model', false);
    this.descriptor.addElement_ivxn3r$('directed_search', false);
    Query$$serializer_instance = this;
  }
  Object.defineProperty(Query$$serializer.prototype, 'descriptor', {
    get: function () {
      return this.descriptor_ce3nwz$_0;
    }
  });
  Query$$serializer.prototype.serialize_awe97i$ = function (encoder, obj) {
    var output = encoder.beginStructure_r0sa6z$(this.descriptor, []);
    output.encodeIntElement_4wpqag$(this.descriptor, 0, obj.ttl);
    output.encodeSerializableElement_blecud$(this.descriptor, 1, QueryModel$$serializer_getInstance(), obj.model);
    output.encodeSerializableElement_blecud$(this.descriptor, 2, DirectedSearch$$serializer_getInstance(), obj.directed_search);
    output.endStructure_qatsm0$(this.descriptor);
  };
  Query$$serializer.prototype.deserialize_nts5qn$ = function (decoder) {
    var index, readAll = false;
    var bitMask0 = 0;
    var local0
    , local1
    , local2;
    var input = decoder.beginStructure_r0sa6z$(this.descriptor, []);
    loopLabel: while (true) {
      index = input.decodeElementIndex_qatsm0$(this.descriptor);
      switch (index) {
        case -2:
          readAll = true;
        case 0:
          local0 = input.decodeIntElement_3zr2iy$(this.descriptor, 0);
          bitMask0 |= 1;
          if (!readAll)
            break;
        case 1:
          local1 = (bitMask0 & 2) === 0 ? input.decodeSerializableElement_s44l7r$(this.descriptor, 1, QueryModel$$serializer_getInstance()) : input.updateSerializableElement_ehubvl$(this.descriptor, 1, QueryModel$$serializer_getInstance(), local1);
          bitMask0 |= 2;
          if (!readAll)
            break;
        case 2:
          local2 = (bitMask0 & 4) === 0 ? input.decodeSerializableElement_s44l7r$(this.descriptor, 2, DirectedSearch$$serializer_getInstance()) : input.updateSerializableElement_ehubvl$(this.descriptor, 2, DirectedSearch$$serializer_getInstance(), local2);
          bitMask0 |= 4;
          if (!readAll)
            break;
        case -1:
          break loopLabel;
        default:throw new UnknownFieldException(index);
      }
    }
    input.endStructure_qatsm0$(this.descriptor);
    return Query_init(bitMask0, local0, local1, local2, null);
  };
  Query$$serializer.prototype.childSerializers = function () {
    return [internal.IntSerializer, QueryModel$$serializer_getInstance(), DirectedSearch$$serializer_getInstance()];
  };
  Query$$serializer.$metadata$ = {
    kind: Kind_OBJECT,
    simpleName: '$serializer',
    interfaces: [GeneratedSerializer]
  };
  var Query$$serializer_instance = null;
  function Query$$serializer_getInstance() {
    if (Query$$serializer_instance === null) {
      new Query$$serializer();
    }
    return Query$$serializer_instance;
  }
  function Query_init(seen, ttl, model, directed_search, serializationConstructorMarker) {
    var $this = Object.create(Query.prototype);
    if ((seen & 1) === 0)
      throw new MissingFieldException('ttl');
    else
      $this.ttl = ttl;
    if ((seen & 2) === 0)
      throw new MissingFieldException('model');
    else
      $this.model = model;
    if ((seen & 4) === 0)
      throw new MissingFieldException('directed_search');
    else
      $this.directed_search = directed_search;
    return $this;
  }
  Query.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'Query',
    interfaces: []
  };
  Query.prototype.component1 = function () {
    return this.ttl;
  };
  Query.prototype.component2 = function () {
    return this.model;
  };
  Query.prototype.component3 = function () {
    return this.directed_search;
  };
  Query.prototype.copy_wpo06n$ = function (ttl, model, directed_search) {
    return new Query(ttl === void 0 ? this.ttl : ttl, model === void 0 ? this.model : model, directed_search === void 0 ? this.directed_search : directed_search);
  };
  Query.prototype.toString = function () {
    return 'Query(ttl=' + Kotlin.toString(this.ttl) + (', model=' + Kotlin.toString(this.model)) + (', directed_search=' + Kotlin.toString(this.directed_search)) + ')';
  };
  Query.prototype.hashCode = function () {
    var result = 0;
    result = result * 31 + Kotlin.hashCode(this.ttl) | 0;
    result = result * 31 + Kotlin.hashCode(this.model) | 0;
    result = result * 31 + Kotlin.hashCode(this.directed_search) | 0;
    return result;
  };
  Query.prototype.equals = function (other) {
    return this === other || (other !== null && (typeof other === 'object' && (Object.getPrototypeOf(this) === Object.getPrototypeOf(other) && (Kotlin.equals(this.ttl, other.ttl) && Kotlin.equals(this.model, other.model) && Kotlin.equals(this.directed_search, other.directed_search)))));
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
  NetworkCom.prototype.onSearch_6hosri$ = function (text, lon, lat) {
    var xmlHttp = {v: new XMLHttpRequest()};
    xmlHttp.v.withCredentials = true;
    xmlHttp.v.open('POST', this.search_uri_0, true);
    xmlHttp.v.setRequestHeader('Content-Type', 'application/json');
    xmlHttp.v.setRequestHeader('Accept', 'application/json');
    xmlHttp.v.onload = NetworkCom$onSearch$lambda(xmlHttp);
    var directed_search = new DirectedSearch();
    var tmp$ = !equals(lon, 'LON');
    if (tmp$) {
      tmp$ = !(lon.length === 0);
    }
    var tmp$_0 = tmp$ && !equals(lat, 'LAT');
    if (tmp$_0) {
      tmp$_0 = !(lat.length === 0);
    }
    if (tmp$_0) {
      directed_search = new DirectedSearch(new DirectedSearch$PlaneTarget(new DirectedSearch$PlaneTarget$GeoLocation(toDouble(lon), toDouble(lat))));
    }
    var query = new Query(3, new QueryModel(text), directed_search);
    var serializer = Query$Companion_getInstance().serializer();
    console.log('QUERY: ', query);
    console.log('QUERY JSON: ', Json.Companion.stringify_tf03ej$(serializer, query));
    xmlHttp.v.send(Json.Companion.stringify_tf03ej$(serializer, query));
  };
  NetworkCom.$metadata$ = {
    kind: Kind_CLASS,
    simpleName: 'NetworkCom',
    interfaces: [SearchEventHandler]
  };
  function main(args) {
    var networkCom = new NetworkCom(document.URL + 'json/search');
    var mainPage = new MainSearchSite('container', 'OEF Search', networkCom);
    mainPage.assemble();
  }
  _.SearchEventHandler = SearchEventHandler;
  _.MainSearchSite = MainSearchSite;
  Object.defineProperty(DirectedSearch$PlaneTarget$GeoLocation, 'Companion', {
    get: DirectedSearch$PlaneTarget$GeoLocation$Companion_getInstance
  });
  Object.defineProperty(DirectedSearch$PlaneTarget$GeoLocation, '$serializer', {
    get: DirectedSearch$PlaneTarget$GeoLocation$$serializer_getInstance
  });
  DirectedSearch$PlaneTarget.GeoLocation = DirectedSearch$PlaneTarget$GeoLocation;
  Object.defineProperty(DirectedSearch$PlaneTarget, 'Companion', {
    get: DirectedSearch$PlaneTarget$Companion_getInstance
  });
  Object.defineProperty(DirectedSearch$PlaneTarget, '$serializer', {
    get: DirectedSearch$PlaneTarget$$serializer_getInstance
  });
  DirectedSearch.PlaneTarget = DirectedSearch$PlaneTarget;
  Object.defineProperty(DirectedSearch, 'Companion', {
    get: DirectedSearch$Companion_getInstance
  });
  Object.defineProperty(DirectedSearch, '$serializer', {
    get: DirectedSearch$$serializer_getInstance
  });
  _.DirectedSearch = DirectedSearch;
  Object.defineProperty(QueryModel, 'Companion', {
    get: QueryModel$Companion_getInstance
  });
  Object.defineProperty(QueryModel, '$serializer', {
    get: QueryModel$$serializer_getInstance
  });
  _.QueryModel = QueryModel;
  Object.defineProperty(Query, 'Companion', {
    get: Query$Companion_getInstance
  });
  Object.defineProperty(Query, '$serializer', {
    get: Query$$serializer_getInstance
  });
  _.Query = Query;
  _.NetworkCom = NetworkCom;
  _.main_kand9s$ = main;
  DirectedSearch$PlaneTarget$GeoLocation$$serializer.prototype.patch_mynpiu$ = GeneratedSerializer.prototype.patch_mynpiu$;
  DirectedSearch$PlaneTarget$$serializer.prototype.patch_mynpiu$ = GeneratedSerializer.prototype.patch_mynpiu$;
  DirectedSearch$$serializer.prototype.patch_mynpiu$ = GeneratedSerializer.prototype.patch_mynpiu$;
  QueryModel$$serializer.prototype.patch_mynpiu$ = GeneratedSerializer.prototype.patch_mynpiu$;
  Query$$serializer.prototype.patch_mynpiu$ = GeneratedSerializer.prototype.patch_mynpiu$;
  main([]);
  Kotlin.defineModule('website', _);
  return _;
}(typeof website === 'undefined' ? {} : website, kotlin, this['kotlinx-serialization-runtime-js']);

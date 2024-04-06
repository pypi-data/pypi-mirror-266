"use strict";

exports.__esModule = true;
exports.DataExplorer = void 0;
var _react = _interopRequireWildcard(require("react"));
var _DataTable = require("./DataTable.js");
var _Search = require("./Search.js");
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { "default": e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && Object.prototype.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n["default"] = e, t && t.set(e, n), n; }
function _extends() { _extends = Object.assign ? Object.assign.bind() : function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; }; return _extends.apply(this, arguments); }
var DataExplorer = exports.DataExplorer = function DataExplorer(_ref) {
  var _ref$data = _ref.data,
    data = _ref$data === void 0 ? [] : _ref$data,
    _ref$dataTypes = _ref.dataTypes,
    dataTypes = _ref$dataTypes === void 0 ? {} : _ref$dataTypes;
  var _useState = (0, _react.useState)([]),
    variables = _useState[0],
    setVariables = _useState[1];
  var _useState2 = (0, _react.useState)({}),
    filters = _useState2[0],
    setFilters = _useState2[1];
  var _useState3 = (0, _react.useState)(data),
    filteredData = _useState3[0],
    setFilteredData = _useState3[1];
  var _useState4 = (0, _react.useState)(""),
    searchStr = _useState4[0],
    setSearchStr = _useState4[1];
  (0, _react.useEffect)(function () {
    if (data.length === 0) {
      return;
    }
    setVariables(Object.keys(data[0]));
    setFilteredData(data);
  }, [data]);
  function inArray(variable, originalArray, item) {
    if (dataTypes[variable].type != "string") {
      if (originalArray.filter(function (a) {
        return a == item;
      }).length === 0) {
        return false;
      } else {
        return originalArray.filter(function (a) {
          return a != item;
        });
      }
    } else {
      if (originalArray.filter(function (a) {
        return a[0] == item[0] && a[1] == item[1];
      }).length === 0) {
        return false;
      } else {
        return originalArray.filter(function (a) {
          return a[0] != item[0] && a[1] != item[1];
        });
      }
    }
    return false;
  }
  function handleFilter(variable, selection, currentFilters) {
    if (currentFilters[variable]) {
      var currentSelection = currentFilters[variable];
      var isInArray = inArray(variable, currentSelection, selection);
      var newSelection;
      if (!isInArray) {
        newSelection = currentSelection.concat([selection]);
      } else {
        newSelection = isInArray;
      }
      if (newSelection.length == 0) {
        delete currentFilters[variable];
      } else {
        currentFilters[variable] = newSelection;
      }
      setFilters(function (currentFilters) {
        return _extends({}, currentFilters);
      });
    } else {
      currentFilters[variable] = [selection];
      setFilters(function (currentFilters) {
        return _extends({}, currentFilters);
      });
    }
  }
  (0, _react.useEffect)(function () {
    var newFilteredData = data.filter(function (d) {
      for (var _i = 0, _Object$keys = Object.keys(d); _i < _Object$keys.length; _i++) {
        var dataVariable = _Object$keys[_i];
        if (dataTypes[dataVariable].type === "string" && d[dataVariable].search(searchStr) != -1) {
          return true;
        }
      }
      return false;
    });
    var allFilteredData = newFilteredData.filter(function (d, i) {
      var _loop = function _loop() {
          var filterVariable = _Object$keys2[_i2];
          var varFilters = filters[filterVariable];
          var dValue = d[filterVariable];
          if (dataTypes[filterVariable].type != "string") {
            if (Array.isArray(dValue)) {
              if (varFilters.filter(function (a) {
                return dValue.indexOf(a) > -1;
              }).length == 0) {
                return {
                  v: false
                };
              }
            } else {
              if (varFilters.filter(function (a) {
                return a == dValue;
              }).length == 0) {
                return {
                  v: false
                };
              }
            }
          }
          if (dataTypes[filterVariable].type == "string") {
            if (varFilters.filter(function (a) {
              return a[0] <= dValue.length && a[1] >= dValue.length;
            }).length == 0) {
              return {
                v: false
              };
            }
          }
        },
        _ret;
      for (var _i2 = 0, _Object$keys2 = Object.keys(filters); _i2 < _Object$keys2.length; _i2++) {
        _ret = _loop();
        if (_ret) return _ret.v;
      }
      return true;
    });
    setFilteredData(allFilteredData);
  }, [filters, searchStr, dataTypes]);
  return /*#__PURE__*/_react["default"].createElement("div", null, /*#__PURE__*/_react["default"].createElement(_Search.Search, {
    setSearchStr: setSearchStr
  }), /*#__PURE__*/_react["default"].createElement(_DataTable.DataTable, {
    data: data,
    filteredData: filteredData,
    dataTypes: dataTypes,
    variables: variables,
    currentFilters: filters,
    handleFilter: handleFilter
  }));
};
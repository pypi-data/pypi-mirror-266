"use strict";

exports.__esModule = true;
exports.InferenceExplorer = void 0;
var _react = _interopRequireWildcard(require("react"));
var _UMAPVis = require("./UMAPVis.js");
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { "default": e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && Object.prototype.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n["default"] = e, t && t.set(e, n), n; }
/* 
Parameters:

trainData - [{"text":, "label"}, ...]
trainDataEmbeddings - [{"0":x, "1":y}, ...]
testData - ["text1", "text2", ...]
testDataEmbeddings - [{"0":x, "1":y}, ...]
testDataPrediction - [{'label':, 'score':}, ...]
*/
var InferenceExplorer = exports.InferenceExplorer = function InferenceExplorer(_ref) {
  var _ref$allTrainData = _ref.allTrainData,
    allTrainData = _ref$allTrainData === void 0 ? [] : _ref$allTrainData,
    _ref$allTestData = _ref.allTestData,
    allTestData = _ref$allTestData === void 0 ? [] : _ref$allTestData,
    _queryInput = _ref._queryInput;
  console.log(allTestData);
  return /*#__PURE__*/_react["default"].createElement("div", null, /*#__PURE__*/_react["default"].createElement(_UMAPVis.UMAPVis, {
    allTrainData: allTrainData,
    allTestData: allTestData,
    _queryInput: _queryInput
  }));
};
"use strict";

exports.__esModule = true;
exports.Search = void 0;
var React = _interopRequireWildcard(require("react"));
var _Box = _interopRequireDefault(require("@mui/material/Box"));
var _IconButton = _interopRequireDefault(require("@mui/material/IconButton"));
var _InputAdornment = _interopRequireDefault(require("@mui/material/InputAdornment"));
var _TextField = _interopRequireDefault(require("@mui/material/TextField"));
var _Search = _interopRequireDefault(require("@mui/icons-material/Search"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { "default": e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && Object.prototype.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n["default"] = e, t && t.set(e, n), n; }
var Search = exports.Search = function Search(_ref) {
  var _ref$title = _ref.title,
    title = _ref$title === void 0 ? "Search" : _ref$title,
    _ref$width = _ref.width,
    width = _ref$width === void 0 ? "350px" : _ref$width,
    setSearchStr = _ref.setSearchStr;
  return /*#__PURE__*/React.createElement(_Box["default"], {
    component: "form",
    sx: {
      '& > :not(style)': {
        m: 1,
        width: '25ch'
      },
      "& .MuiOutlinedInput-root": {
        "& fieldset": {
          "borderRadius": "25px"
        }
      }
    },
    noValidate: true,
    autoComplete: "off"
  }, /*#__PURE__*/React.createElement(_TextField["default"], {
    InputProps: {
      startAdornment: /*#__PURE__*/React.createElement(_InputAdornment["default"], {
        position: "start"
      })
    },
    size: "small",
    id: "outlined-basic",
    label: title,
    variant: "outlined",
    onChange: function onChange(event) {
      setSearchStr(event.target.value);
    },
    style: {
      "width": width
    }
  }));
};
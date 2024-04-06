"use strict";

exports.__esModule = true;
exports.DataTable = void 0;
var React = _interopRequireWildcard(require("react"));
var _Box = _interopRequireDefault(require("@mui/material/Box"));
var _Table = _interopRequireDefault(require("@mui/material/Table"));
var _TableBody = _interopRequireDefault(require("@mui/material/TableBody"));
var _TableCell = _interopRequireDefault(require("@mui/material/TableCell"));
var _TableContainer = _interopRequireDefault(require("@mui/material/TableContainer"));
var _TableHead = _interopRequireDefault(require("@mui/material/TableHead"));
var _TablePagination = _interopRequireDefault(require("@mui/material/TablePagination"));
var _TableRow = _interopRequireDefault(require("@mui/material/TableRow"));
var _TableSortLabel = _interopRequireDefault(require("@mui/material/TableSortLabel"));
var _Typography = _interopRequireDefault(require("@mui/material/Typography"));
var _Paper = _interopRequireDefault(require("@mui/material/Paper"));
var _FormControlLabel = _interopRequireDefault(require("@mui/material/FormControlLabel"));
var _utils = require("@mui/utils");
var _HistogramVis = require("./HistogramVis.js");
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { "default": e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && Object.prototype.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n["default"] = e, t && t.set(e, n), n; }
// Adapted from https://mui.com/material-ui/react-table/

function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}
function getComparator(order, orderBy) {
  return order === 'desc' ? function (a, b) {
    return descendingComparator(a, b, orderBy);
  } : function (a, b) {
    return -descendingComparator(a, b, orderBy);
  };
}

// Since 2020 all major browsers ensure sort stability with Array.prototype.sort().
// stableSort() brings sort stability to non-modern browsers (notably IE11). If you
// only support modern browsers you can replace stableSort(exampleArray, exampleComparator)
// with exampleArray.slice().sort(exampleComparator)
function stableSort(array, comparator) {
  array.sort(function (a, b) {
    var order = comparator(a, b);
    if (order !== 0) {
      return order;
    }
    return a - b;
  });
  return array.map(function (el) {
    return el;
  });
}
function EnhancedTableHead(_ref) {
  var _ref$variables = _ref.variables,
    variables = _ref$variables === void 0 ? [] : _ref$variables,
    _ref$data = _ref.data,
    data = _ref$data === void 0 ? [] : _ref$data,
    _ref$dataTypes = _ref.dataTypes,
    dataTypes = _ref$dataTypes === void 0 ? {} : _ref$dataTypes,
    currentFilters = _ref.currentFilters,
    handleFilter = _ref.handleFilter,
    onRequestSort = _ref.onRequestSort,
    order = _ref.order,
    orderBy = _ref.orderBy,
    rowCount = _ref.rowCount;
  function createSortHandler(property) {
    return function (e) {
      onRequestSort(e, property);
    };
  }
  return /*#__PURE__*/React.createElement(_TableHead["default"], null, /*#__PURE__*/React.createElement(_TableRow["default"], null, variables.map(function (v) {
    return /*#__PURE__*/React.createElement(_TableCell["default"], {
      key: v,
      padding: "normal",
      sortDirection: orderBy === v.id ? order : false
    }, /*#__PURE__*/React.createElement(_TableSortLabel["default"], {
      active: orderBy === v,
      direction: orderBy === v ? order : 'asc',
      onClick: createSortHandler(v)
    }, /*#__PURE__*/React.createElement("p", {
      style: {
        "margin": "0 0 0 5px"
      }
    }, v, /*#__PURE__*/React.createElement("span", {
      style: {
        "margin": "0 0 0 10px",
        "color": "gray"
      }
    }, /*#__PURE__*/React.createElement("i", null, "- " + (dataTypes[v].type == "string" ? "string (length)" : dataTypes[v].type)))), orderBy === v ? /*#__PURE__*/React.createElement(_Box["default"], {
      component: "span",
      sx: _utils.visuallyHidden
    }, order === 'desc' ? 'sorted descending' : 'sorted ascending') : null), /*#__PURE__*/React.createElement(_HistogramVis.HistogramVis, {
      data: data,
      dataTypes: dataTypes,
      variable: v,
      currentFilters: currentFilters,
      handleFilter: handleFilter
    }));
  })));
}
var DataTable = exports.DataTable = function DataTable(_ref2) {
  var _ref2$data = _ref2.data,
    data = _ref2$data === void 0 ? [] : _ref2$data,
    _ref2$filteredData = _ref2.filteredData,
    filteredData = _ref2$filteredData === void 0 ? [] : _ref2$filteredData,
    _ref2$dataTypes = _ref2.dataTypes,
    dataTypes = _ref2$dataTypes === void 0 ? {} : _ref2$dataTypes,
    _ref2$variables = _ref2.variables,
    variables = _ref2$variables === void 0 ? [] : _ref2$variables,
    currentFilters = _ref2.currentFilters,
    handleFilter = _ref2.handleFilter;
  var _React$useState = React.useState("asc"),
    order = _React$useState[0],
    setOrder = _React$useState[1];
  var _React$useState2 = React.useState("text"),
    orderBy = _React$useState2[0],
    setOrderBy = _React$useState2[1];
  var _React$useState3 = React.useState(0),
    page = _React$useState3[0],
    setPage = _React$useState3[1];
  var _React$useState4 = React.useState(10),
    rowsPerPage = _React$useState4[0],
    setRowsPerPage = _React$useState4[1];
  function handleRequestSort(e, property) {
    var isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  }
  var handleChangePage = function handleChangePage(event, newPage) {
    setPage(newPage);
  };
  var handleChangeRowsPerPage = function handleChangeRowsPerPage(event) {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Avoid a layout jump when reaching the last page with empty rows.
  var emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - data.length) : 0;
  var visibleRows = React.useMemo(function () {
    return stableSort(filteredData, getComparator(order, orderBy)).slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  }, [order, orderBy, page, rowsPerPage, data, filteredData]);
  React.useEffect(function () {
    setPage(0);
  }, [filteredData]);
  return /*#__PURE__*/React.createElement(_Box["default"], null, /*#__PURE__*/React.createElement(_Paper["default"], {
    sx: {
      mb: 2,
      "width": "1000px"
    }
  }, /*#__PURE__*/React.createElement(_TableContainer["default"], null, /*#__PURE__*/React.createElement(_Table["default"], {
    "aria-labelledby": "tableTitle",
    size: "small"
  }, /*#__PURE__*/React.createElement(EnhancedTableHead, {
    data: data,
    dataTypes: dataTypes,
    order: order,
    orderBy: orderBy,
    onRequestSort: handleRequestSort,
    rowCount: data.length,
    variables: variables,
    currentFilters: currentFilters,
    handleFilter: handleFilter
  }), /*#__PURE__*/React.createElement(_TableBody["default"], null, visibleRows.map(function (row, index) {
    var labelId = "enhanced-table-checkbox-" + index;
    return /*#__PURE__*/React.createElement(_TableRow["default"], {
      hover: true,
      role: "checkbox",
      tabIndex: -1,
      key: "" + index,
      sx: {
        cursor: 'pointer'
      }
    }, variables.map(function (v, i) {
      return /*#__PURE__*/React.createElement(_TableCell["default"], {
        key: "row" + index + "cell" + i
      }, Array.isArray(row[v]) ? "" + row[v].join(", ") : row[v]);
    }));
  }), emptyRows > 0 && /*#__PURE__*/React.createElement(_TableRow["default"], {
    style: {
      height: 33 * emptyRows
    }
  }, /*#__PURE__*/React.createElement(_TableCell["default"], {
    colSpan: 6
  }))))), /*#__PURE__*/React.createElement(_TablePagination["default"], {
    rowsPerPageOptions: [10, 20, 30],
    component: "div",
    count: filteredData.length,
    rowsPerPage: rowsPerPage,
    page: page,
    onPageChange: handleChangePage,
    onRowsPerPageChange: handleChangeRowsPerPage
  })));
};
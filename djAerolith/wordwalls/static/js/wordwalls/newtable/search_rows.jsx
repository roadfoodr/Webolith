import React from 'react';
import PropTypes from 'prop-types';

import SearchRow, { SearchTypesEnum } from './search_row';

const SearchRows = props => (
  props.searches.map((search, idx) => (
    <SearchRow
      // To suppress idx warning we use idx + 0, ew. XXX
      key={`row${idx + 0}`}
      index={idx}
      searchType={search.searchType}
      minValue={search.minValue}
      maxValue={search.maxValue}
      minAllowedValue={SearchTypesEnum.properties[search.searchType].minAllowed}
      maxAllowedValue={SearchTypesEnum.properties[search.searchType].maxAllowed}
      valueList={search.valueList}
      addRow={props.addSearchRow}
      removeRow={props.removeSearchRow}
      removeDisabled={idx === 0 && props.searches.length === 1}
      modifySearchType={props.modifySearchType}
      modifySearchParam={props.modifySearchParam}
    />))
);

SearchRows.propTypes = {
  searches: PropTypes.arrayOf(PropTypes.shape({
    searchType: PropTypes.number,
    minValue: PropTypes.number,
    maxValue: PropTypes.number,
    minAllowedValue: PropTypes.number,
    maxAllowedValue: PropTypes.number,
    valueList: PropTypes.string,
  })).isRequired,
  modifySearchType: PropTypes.func.isRequired,
  modifySearchParam: PropTypes.func.isRequired,
  addSearchRow: PropTypes.func.isRequired,
  removeSearchRow: PropTypes.func.isRequired,
};

export default SearchRows;
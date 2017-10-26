import React from 'react';
import PropTypes from 'prop-types';

import Select from '../forms/select';
import SearchRow, { SearchTypesEnum } from './search_row';
// Questions per round && time per round
// function genWordLengthOptions() {
//   return [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15].map(el => ({
//     value: String(el),
//     displayValue: String(el),
//   }));
// }

class WordSearchDialog extends React.Component {
  // constructor() {
  //   super();
  //   this.handleMinProbChange = this.handleMinProbChange.bind(this);
  //   this.handleMaxProbChange = this.handleMaxProbChange.bind(this);
  // }

  // getMaxProbForLength(wordLength) {
  //   const foundLex = this.props.availableLexica.find(
  //     lex => lex.id === this.props.lexicon);
  //   return foundLex.lengthCounts[wordLength];
  // }

  // handleMinProbChange(event) {
  //   let min = parseInt(event.target.value, 10);
  //   if (Number.isNaN(min)) {
  //     min = '';
  //   }
  //   this.props.onSearchParamChange('probMin', String(min));
  // }

  // handleMaxProbChange(event) {
  //   let max = parseInt(event.target.value, 10);
  //   if (Number.isNaN(max)) {
  //     max = '';
  //   }
  //   // From the length counts, limit max probability.
  //   const maxProbForLength = this.getMaxProbForLength(this.props.wordLength);
  //   if (max > maxProbForLength) {
  //     max = maxProbForLength;
  //   }
  //   this.props.onSearchParamChange('probMax', String(max));
  // }


/**
 *           <Select
            colSize={4}
            label="Word Length"
            selectedValue={String(this.props.wordLength)}
            onChange={event => this.props.onSearchParamChange('wordLength',
              parseInt(event.target.value, 10))}
            options={genWordLengthOptions()}
          />
          <NumberInput
            colSize={4}
            label="Probability (min 1)"
            value={this.props.probMin}
            onChange={this.handleMinProbChange}
          />
          <NumberInput
            colSize={4}
            label={`Probability (max ${maxProbForLength})`}
            value={this.props.probMax}
            onChange={this.handleMaxProbChange}
          />
 */

  searchRows() {
    const rows = this.props.searches.map((search, idx) => (
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
        addRow={this.props.addSearchRow}
        removeRow={this.props.removeSearchRow}
        removeDisabled={idx === 0 && this.props.searches.length === 1}
        modifySearchType={this.props.onSearchTypeChange}
        modifySearchParam={this.props.onSearchParamChange}
      />));
    return rows;
  }

  render() {
    // const maxProbForLength = this.getMaxProbForLength(this.props.wordLength);
    return (
      <div className="row" style={{ marginTop: '8px' }}>
        <div className="col-sm-8">
          {this.searchRows()}
          <Select
            colSize={4}
            label="Mode"
            badge="New!"
            selectedValue={this.props.multiplayerOn ? 'multi' : 'single'}
            options={[{ value: 'single', displayValue: 'Single Player' },
                      { value: 'multi', displayValue: 'Multiplayer' }]}
            onChange={e => this.props.onMultiplayerModify(e.target.value === 'multi')}
          />
          <button
            className="btn btn-primary"
            style={{ marginTop: '0.75em' }}
            onClick={this.props.onSearchSubmit}
            data-dismiss="modal"
          >Play!
          </button>
          <button
            className="btn btn-info"
            style={{ marginTop: '0.75em', marginLeft: '1em' }}
            onClick={this.props.onFlashcardSubmit}
            data-dismiss="modal"
          >Flashcard
          </button>
        </div>
      </div>
    );
  }
}

WordSearchDialog.propTypes = {
  searches: PropTypes.arrayOf(PropTypes.shape({
    searchType: PropTypes.number,
    minValue: PropTypes.number,
    maxValue: PropTypes.number,
    minAllowedValue: PropTypes.number,
    maxAllowedValue: PropTypes.number,
    valueList: PropTypes.string,
  })).isRequired,
  onSearchTypeChange: PropTypes.func.isRequired,
  onSearchParamChange: PropTypes.func.isRequired,
  addSearchRow: PropTypes.func.isRequired,
  removeSearchRow: PropTypes.func.isRequired,
  onSearchSubmit: PropTypes.func.isRequired,
  onFlashcardSubmit: PropTypes.func.isRequired,
  // availableLexica: PropTypes.arrayOf(PropTypes.shape({
  //   id: PropTypes.number,
  //   lexicon: PropTypes.string,
  //   description: PropTypes.string,
  //   counts: PropTypes.object,
  // })),
  // lexicon: PropTypes.number,
  multiplayerOn: PropTypes.bool.isRequired,
  onMultiplayerModify: PropTypes.func.isRequired,
};

export default WordSearchDialog;
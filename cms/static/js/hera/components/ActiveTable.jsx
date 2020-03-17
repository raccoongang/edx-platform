import React from 'react';


class TableCell extends React.Component{
    render() {
        if (this.props.type === 'head') {
            return <th>{this.props.children}</th>;
        }
        return <td>{this.props.children}</td>;
    }
}


export default class ActiveTable extends React.PureComponent{

    constructor(props) {
        super(props);

        this.changeCell = this.changeCell.bind(this);
        this.changeCellType = this.changeCellType.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.addColumn = this.addColumn.bind(this);
        this.removeColumn = this.removeColumn.bind(this);
        this.addRow = this.addRow.bind(this);
        this.removeRow = this.removeRow.bind(this);
    }

    changeCell(event, col_idx, row_idx) {
        const value = event.target.value;
        let {columns, rows} = this.getData();
        if (row_idx === undefined) { // means we change column title
            columns = columns.map((col, c_idx) => {
                if (c_idx === col_idx) {
                    col.value = value;
                    return col;
                }
                return col;
            });
            
        } else {
            rows = rows.map((row, idx) => {
                if (idx === row_idx) {
                    row[col_idx].value = value;
                    return row;
                }
                return row;
            });
        }
        this.props.saveHandler({
            columns, rows
        }, this.props.problemTypeIndex);
    }

    handleKeyPress(event, col_idx, row_idx) {
        if (event.key === 'Enter') {
            this.changeCellType(event, col_idx, row_idx);
            document.activeElement.blur();
        }
    }

    changeCellType(event, col_idx, row_idx) {
        const value = event.target.value;
        let {columns, rows} = this.getData();
        if (row_idx === undefined) {
            columns = columns.map((col, c_idx) => {
                if (c_idx === col_idx) {
                    const newCol = {...col};
                    if (value.startsWith('!')) {
                        newCol.type = 'head';
                    } else {
                        newCol.type = '';
                    }
                    return newCol;
                }
                return col;
            });
        } else {
            rows = rows.map((row, idx) => {
                if (idx === row_idx) {
                    const newRow = {...row};
                    if (newRow[col_idx].value.startsWith('!')) {
                        newRow[col_idx].type = 'head';
                    } else {
                        newRow[col_idx].type = '';
                    }
                    return newRow;
                }
                return row;
            });
        }
        this.props.saveHandler({
            columns, rows
        }, this.props.problemTypeIndex);
    }

    addColumn(col_idx) {
        let {columns, rows} = this.getData();
        columns.splice(col_idx, 0, {value: '', type: ''});
        if (col_idx === columns.length -1) {
            rows = rows.map((row, r_idx) => {
                row[col_idx] = {value: ''};
                return row;
            });
        } else { // move all indexes forward
            rows = rows.map((row, r_idx) => {
                let newRow = {};
                for (let i in Object.keys(row)) {
                    if (+i >= col_idx) {
                        newRow[+i+1] = row[+i];
                    } else {
                        newRow[+i] = row[+i];
                    }
                }
                newRow[col_idx] = {value: ''};
                return newRow;
            });
        }
        this.props.saveHandler({
            columns, rows
        }, this.props.problemTypeIndex);
    }

    addRow(r_idx) {
        let {rows, columns} = this.getData();
        let emptyRow = {};
        columns.map((col, c_idx) => {
            emptyRow[c_idx] = {value: ''};
        });
        if (r_idx === undefined) {
            rows = rows.concat([emptyRow]);
        } else {
            rows.splice(r_idx, 0, emptyRow);
        }
        this.props.saveHandler({
            columns, rows
        }, this.props.problemTypeIndex);
    }

    removeRow(row_idx) {
        const rows = this.getData().rows.filter((row, r_idx) => {
            return row_idx !== r_idx;
        });
        this.props.saveHandler({
            columns: this.getData().columns, rows
        }, this.props.problemTypeIndex);
    }

    removeColumn(col_idx) {
        let {columns, rows} = this.getData();
        if (col_idx === columns.length -1) {
            rows = rows.map((row, r_idx) => {
                delete row[col_idx];
                return row;
            });
        } else { // move all indexes backward
            rows = rows.map((row, r_idx) => {
                let newRow = {};
                for (let i in Object.keys(row)) {
                    if (+i > col_idx) {
                        newRow[+i-1] = row[+i];
                    } else {
                        newRow[+i] = row[+i];
                    }
                }
                return newRow;
            });
        }
        columns = columns.filter((col, c_idx) => {
            return col_idx !== c_idx;
        });
        this.props.saveHandler({
            columns, rows
        }, this.props.problemTypeIndex);
    }

    getData() {
        let {columns, rows} = this.props.tableData;
        if (!columns || !rows) {
            columns = [{value: '', type: ''}]
            rows = [{0: {value: '', type: ''}}]
        }
        return {
            columns, rows
        };
    }

    render() {
        const {columns, rows} = this.getData();
        return (
            <div>
                <div className="table-description">
                    <p>
                        Use '<b>!</b>' to make cell of the table as a header (e.g. !text).
                    </p>
                    <p>
                        Use '<b>?</b>' to make cell editable for the student answers (e.g. ?text).
                    </p>
                </div>
                <div className="table-wrapper">
                    <table>
                        <tbody>
                        <tr>
                            {
                                columns.map((column, idx) => {
                                    return  (
                                        <TableCell key={idx} type={column.type}>
                                            <input
                                                type="text"
                                                value={column.value}
                                                onBlur={(event)=>{this.changeCellType(event, idx)}}
                                                onKeyPress={(event)=>{this.handleKeyPress(event, idx)}}
                                                onChange={(event)=>{this.changeCell(event, idx)}}
                                            />
                                            <div className="table-buttons">
                                                <button type="button" className="table-buttons__btn is-add" onClick={() => {this.addColumn(idx+1)}}>+</button>
                                                {
                                                    columns.length > 1 && (
                                                        <button type="button" className="table-buttons__btn is-remove" onClick={() => {this.removeColumn(idx)}}>-</button>
                                                    )
                                                }
                                            </div>
                                        </TableCell>
                                    )
                                })
                            }
                        </tr>
                        {
                            rows && rows.map((row, r_idx) => {
                                return (
                                    <tr key={r_idx}>
                                        {
                                            columns.map((column, c_idx) => {
                                                return (
                                                    <TableCell key={c_idx} type={row[c_idx].type}>
                                                        <input
                                                            type="text"
                                                            value={row[c_idx].value}
                                                            onChange={(event)=>{this.changeCell(event, c_idx, r_idx)}}
                                                            onBlur={(event)=>{this.changeCellType(event, c_idx, r_idx)}}
                                                            onKeyPress={(event)=>{this.handleKeyPress(event, c_idx, r_idx)}}
                                                        />
                                                    </TableCell>
                                                )
                                            })
                                        }
                                        <td>
                                            <div className="table-buttons">
                                                <button type="button" className="table-buttons__btn is-add" onClick={() => {this.addRow(r_idx+1)}}>+</button>
                                                {
                                                    rows.length > 1 && (
                                                        <button type="button" className="table-buttons__btn is-remove" onClick={() => {this.removeRow(r_idx)}}>-</button>
                                                    )
                                                }
                                            </div>
                                        </td>
                                    </tr>
                                )
                            })
                        }
                        </tbody>
                    </table>
                </div>
            </div>
        )
    }
}

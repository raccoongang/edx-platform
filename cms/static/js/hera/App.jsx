import { Provider } from 'react-redux';
import React from 'react';
import ReactDOM from 'react-dom';

import store from './store/store';

import TeacherTemplate from './containers/TeacherTemplate';

import {_post} from './utils/api';


export class HeraApp extends React.Component{

    createSubsection() {
        return _post('/xblock/hera_template_create_handler', store.getState());
    }

    saveChanges() {
        return _post('/xblock/hera_template_changes_handler', store.getState());
    }

    render() {
        return (
            <Provider store={store}>
                <TeacherTemplate createSubsection={this.createSubsection} saveChanges={this.saveChanges}/>
            </Provider>
        )
    }
}

import { Provider } from 'react-redux';
import React from 'react';
import ReactDOM from 'react-dom';

import store from './store/store';

import TeacherTemplate from './containers/TeacherTemplate';


export class HeraApp extends React.Component{
    render() {
        return (
            <Provider store={store}>
                <TeacherTemplate/>
            </Provider>
        )
    }
}

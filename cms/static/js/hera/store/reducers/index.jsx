import { combineReducers } from 'redux';

import TitleReducer from './TitleReducer';
import QuestionsReducer from './QuestionsReducer';
import IntroductionReducer from './IntroductionReducer';
import SimulationReducer from './SimulationReducer';
import SubsectionDataReducer from './SubsectionDataReducer';
import EndSurvey from './EndSurveyReducer';
import LessonSummary from "./LessonSummaryReducer";

var reducers = combineReducers({
    title: TitleReducer,
    introduction: IntroductionReducer,
    simulation: SimulationReducer,
    questions: QuestionsReducer,
    subsectionData: SubsectionDataReducer,
    endSurvey: EndSurvey,
    lessonSummary: LessonSummary,
});

export default reducers;

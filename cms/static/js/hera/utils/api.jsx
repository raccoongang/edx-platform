import cookie from 'react-cookies';
import axios from 'axios';

const ROOT_URL = '/xblock/';

const HEADERS = {
    'Content-Type': 'application/json',
    'X-CSRFToken': cookie.load('csrftoken'),
};

const defaultParams = {headers: HEADERS, withCredentials: true};

const _post = (url, data) => {
    return axios.post(url, data, defaultParams);
};

/**
 * Create new element for parent.
 * TODO: add whole description.
 * 
 * @param {*} parentLocator 
 * @param {*} category 
 * @param {*} displayName 
 */
export const addElement = (parentLocator, category, displayName) => {
    const data = {
        category: category,
        parent_locator: parentLocator,
        display_name: displayName
    }
    return _post(ROOT_URL, data);
};


// {
//     imgUrl: "link",
//     iframeUrl: "link",
//     description: "html content",
//     options: [
//         {
//             correct: true/false,
//             title: "title text" // assume this will be the unique identificator
//         },
//         {
//             correct: true/false,
//             title: "title text" // assume this will be the unique identificator
//         }
//     ],
//     userConfidence: "int",
//     confidenceText: "some text",
//     correctAnswerText: "The correct answer text",
//     incorrectAnswerText: "An incorrect answer text",
//     rephrase: {
//         imgUrl: "link",
//         content: "html content"
//     },
//     breakDown: : {
//         imgUrl: "link",
//         content: "html content"
//     },
//     teachMe: : {
//         imgUrl: "link",
//         content: "html content"
//     }
// }

// {
//     imgUrl: "link",
//     iframeUrl: "link",
//     sliderBar: [
//         {
//             content: "html content"
//         },
//         {
//             content: "html content"
//         },
//         {
//             content: "html content"
//         }
//     ]
// }




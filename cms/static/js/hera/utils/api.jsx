import cookie from 'react-cookies';
import axios from 'axios';

const XBLOCK_ROOT_URL = '/xblock/';

const HEADERS = {
    'Content-Type': 'application/json',
    'X-CSRFToken': cookie.load('csrftoken'),
};

const defaultParams = {headers: HEADERS, withCredentials: true};

const _post = (url, data) => {
    return axios.post(url, data, defaultParams);
};

const _get = (url) => {
    return axios.get(url, {}, defaultParams);
}

/**
 * Create new element for parent.
 * TODO: add whole description.
 * 
 * @param {*} parentLocator 
 * @param {*} category 
 * @param {*} displayName 
 */
export const addSubsection = (parentLocator, category, displayName) => {
    const data = {
        category: category,
        parent_locator: parentLocator,
        display_name: displayName
    };
    return _post(XBLOCK_ROOT_URL, data);
};

export const getData = (locator) => {
    return _get(XBLOCK_ROOT_URL + locator).then(response => {
        return response.data;
    });
};

export const getXblockData = (xBlockId) => {
    return _post(XBLOCK_ROOT_URL + xBlockId + '/handler/get_data', {});
    // .then(response => {
        // return {
        //     xBlockId: xBlockId,
        //     ...response.data
        // };
    // });
}

// export const getSectionData = (sectionLocation) => {
//     return _get(XBLOCK_ROOT_URL + sectionLocation);
// };

/**
 * parent_locator: "locator"
 * category: "vertical"
 * display_name: "Unit"
 */
export const createUnit = (parentLocator) => {
    const data = {
        parent_locator: parentLocator,
        category: "vertical",
        display_name: "Unit"
    };
    return _post(XBLOCK_ROOT_URL, data);
};

/**
 *  Create xblock.
 *  For Introduction, Simulation
 * reponse = 
 *      locator
 *      courseKey
 * 
 * @param {response} parentLocator 
 * @param {*} category 
 */
export const createIntroductionXBlock = (parentLocator) => {
    const data = {
        parent_locator: parentLocator,
        category: "hera_pages",
    };
    return _post(XBLOCK_ROOT_URL, data);
};

/**
 * {"values":{"data":{"display_name":"example"}},"defaults":[]}
 * 
 * 
 * @param {*} locator 
 */
export const saveIntroductionXBlockData = (locator, data) => {
    const postData = {
        values: {
            data: data
        }
    };
    return _post(XBLOCK_ROOT_URL + locator + "/handler/submit_studio_edits", postData);
}


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
//     },
//     question: {
//         questionType: '', // ['radio', 'checkbox', 'select', 'number', 'text']
//         // 'radio', 'checkbox', 'select'
//         options: [
//             {
//                 correct: true/false,
//                 title: "title text" // assume this will be the unique identificator
//             },
//             {
//                 correct: true/false,
//                 title: "title text" // assume this will be the unique identificator
//             }
//         ],
//         answer: text/number,
//         preciseness: text // +-5, +-0.001, +-0.1% 
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




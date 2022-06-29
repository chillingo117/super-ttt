const axios = require('axios');
const BASE_URL = "http://localhost:5000/";


class Api{
    constructor(axiosInstance) {
        this.axiosInstance = axiosInstance;
    }

    createGame()
    {
        return this.axiosInstance.post('/game/create')
            .then(response => response.data);
    }

    getGame(id)
    {
        return this.axiosInstance.get('/game', {params: {id: id}})
            .then(response => response.data);
    }
    
    deleteGame(id)
    {
        return this.axiosInstance.delete('/game', {params: {id: id}})
            .then(response => response.data);
    }
    
    playGame(id, index)
    {
        return this.axiosInstance.post('/game/play', null, { params: {id:id, index:index} })
            .then(response => response.data);
    }

    playGameAi(id)
    {
        return this.axiosInstance.post('/game/play/ai', null, { params: {id:id} })
            .then(response => response.data);
    }

    pingGame(id)
    {
        return this.axiosInstance.get('/game/ping', {params: {id: id}})
            .then(response => response.data);
    }
    
    jumpTo(id, step)
    {
        return this.axiosInstance.post('/game/jump', null, { params: {id:id, step:step} })
            .then(response => response.data);
    }
}

export default function CreateApiInstance(){
    let axiosInstance = axios.create({
        baseURL: BASE_URL,
        timeout: 10000,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        },
    })

    return new Api(axiosInstance);
}


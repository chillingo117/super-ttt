import React from 'react';
import './index.css';
import CreateApiInstance from './api';
import {Grid, Box, Stack, Button, Typography} from "@mui/material";
import {HowToPlay} from "./howToPlay";

function convertToSymbol(squareValue) {
    switch (squareValue){
        case 1:
            return "X";
        case -1:
            return "O";
        default:
            return "";
    }
}

function setStateFromResponse(game, response){
    game.setState({
        subBoards: response.subBoards,
        currentBoard: response.currentSubBoard,
        currentPlayer: response.currentPlayer,
        stepNumber: response.historyLength - 1,
        winner: response.winner,
    })
}

class Square extends React.Component {
    render(){
        let style;
        if(this.props.winner === this.props.value && this.props.value !== 0)
            style = { border: 3, borderColor: "Green"};
        else
            style = { border: 1, borderColor: "Black" };

        return (
            <Button sx={style} className="square" onClick={this.props.onClick}>
                {convertToSymbol(this.props.value)}
            </Button>
        );
    }
}

class SubBoard extends React.Component {
    renderSquare(squareIndex) {
        return (
            <Square
                value={this.props.squares[squareIndex]}
                winner={this.props.winner}
                onClick={() => this.props.onClick(squareIndex)}
            />
        );
    }

    render() {
        let style;
        if(this.props.isCurrent)
        {
            console.log(this.props.squares);
            if(this.props.squares.every(value => value !== 0))
                style = { border: 3, borderColor: "Blue"};
            else
                style = { border: 3, borderColor: "Red"};
        }
        else
            style = { border: 3 };

        return (
            <Box sx={style}>
                <Stack>
                    <Grid item className="board-row">
                        <Stack direction="row">
                            <div>{this.renderSquare(0)}</div>
                            <div>{this.renderSquare(1)}</div>
                            <div>{this.renderSquare(2)}</div>
                        </Stack>
                    </Grid>
                    <Grid item className="board-row">
                        <Stack direction="row">
                            <div>{this.renderSquare(3)}</div>
                            <div>{this.renderSquare(4)}</div>
                            <div>{this.renderSquare(5)}</div>
                        </Stack>
                    </Grid>
                    <Grid item className="board-row">
                        <Stack direction="row">
                            <div>{this.renderSquare(6)}</div>
                            <div>{this.renderSquare(7)}</div>
                            <div>{this.renderSquare(8)}</div>
                        </Stack>
                    </Grid>
                </Stack>
            </Box>
        );
    }
}

class SuperBoard extends React.Component {
    renderSubBoard(subBoardIndex) {
        return (
            <SubBoard
                isCurrent={this.props.currentBoard === subBoardIndex}
                squares={this.props.subBoards[subBoardIndex].squares}
                winner={this.props.subBoards[subBoardIndex].winner}
                onClick={squareIndex => this.props.onClick(subBoardIndex, squareIndex)}
            />
        );
    }
    render() {
        return (
            <Stack>
                <Grid item className="super-board-row">
                    <Stack direction="row">
                        <div>{this.renderSubBoard(0)}</div>
                        <div>{this.renderSubBoard(1)}</div>
                        <div>{this.renderSubBoard(2)}</div>
                    </Stack>
                </Grid>
                <Grid item className="super-board-row">
                    <Stack direction="row">
                        <div>{this.renderSubBoard(3)}</div>
                        <div>{this.renderSubBoard(4)}</div>
                        <div>{this.renderSubBoard(5)}</div>
                    </Stack>
                </Grid>
                <Grid item className="super-board-row">
                    <Stack direction="row">
                        <div>{this.renderSubBoard(6)}</div>
                        <div>{this.renderSubBoard(7)}</div>
                        <div>{this.renderSubBoard(8)}</div>
                    </Stack>
                </Grid>
            </Stack>
        );
    }
}

export default class Game extends React.Component {
    constructor(props) {
        super(props);
        this.loading = true;
        this.state = null;
        this.gameID = null;
        this.api = CreateApiInstance();
        this.newGame();
        this.preparePing();
    }

    preparePing() {
        setTimeout(() => {
            if(this.gameID != null){
                this.api.pingGame(this.gameID).then(() => this.preparePing());
            }
            else
            {
                this.preparePing();
            }
        }, 10000);
    }

    newGame(){
        this.api.createGame()
            .then(gameID => {
                this.gameID = gameID;
                return gameID;
            })
            .then(gameID => {
                return this.api.getGame(gameID);
            })
            .then(response => {
                setStateFromResponse(this, response)
                this.loading = false;
            });
    }

    handleClick(subBoardIndex, squareIndex) {
        if (this.state.winner !== 0
            || subBoardIndex !== this.state.currentBoard) {
            return;
        }

        this.loading = true;
        this.api.playGame(this.gameID, squareIndex)
            .then(response => {
                setStateFromResponse(this, response)
                this.loading = false;
            })
    }

    jumpTo(step) {
        this.loading = true;
        this.api.jumpTo(this.gameID, step)
            .then(response => {
                console.log(response)
                setStateFromResponse(this, response)
                this.loading = false;
            });
    }
    
    aiPlay(){
        this.loading = true;
        this.api.playGameAi(this.gameID)
            .then(response => {
                console.log(response)
                setStateFromResponse(this, response)
                this.loading = false;
            });
    }

    render() {
        if(!this.loading)
        {
            const winner = this.state.winner;
            const moves = [...Array(this.state.stepNumber+1).keys()].map((move) => {
                const desc = move > 0 ?
                    'Go to move #' + move :
                    'Go to game start';
                return (
                    <li key={move}>
                        <button onClick={() => this.jumpTo(move)}>{desc}</button>
                    </li>
                );
            });

            let status;
            let style;
            if (winner !== 0) {
                status = "Winner: " + convertToSymbol(winner);
                style = { border: 3, borderColor: "Green"};
            } else {
                status = "Next player: " + (this.state.currentPlayer === 1 ? "X" : "O");
                style = { border: 1, borderColor: "Black"};
            }

            return (
                <Box sx={{ flexGrow: 1 }}>
                    <Stack direction="row" className="game" >
                        <Stack>
                            <SuperBoard
                                currentBoard={this.state.currentBoard}
                                subBoards={this.state.subBoards}
                                onClick={(subBoardIndex, squareIndex) => this.handleClick(subBoardIndex, squareIndex)}
                            />
                            <Typography sx={style} className="status">{status}</Typography>
                            <button onClick={() => this.aiPlay()}>Make Ai Move</button>
                            <HowToPlay/>
                        </Stack>
                        <Stack>
                            <ol>{moves}</ol>
                        </Stack>

                    </Stack>
                </Box>
            );
        }
        else{
            return(<div>loading</div>);
        }
    }
}

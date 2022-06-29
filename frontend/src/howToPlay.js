export function HowToPlay() {
    return (
        <div>
            The whole 9x9 board is the 'super board'.<br/>
            Each inner 3x3 board is a 'sub board'.<br/>
                
            The current sub board of play is highlighted.<br/>
                
            When outlined red, click on a space inside to place your symbol.<br/>
            When outlined blue, click to select which board to move to next.<br/>
            &nbsp;&nbsp;&nbsp;&nbsp; -- It will still be your turn after you have selected.<br/>
            When someone wins a board, that board can still be visited via a different board.<br/>
                
            To win, connect a line of 3 sub boards.
        </div>
    );
}

import './Explaination.css';

function Explaination() {
    return (
        <div className="explanation-container">
            <h3 className="explanation-title">How to use the Maths Online Tutoring Tool</h3>
            <div className="explanation-content">
                <p>To use the tool, you can either upload an image of the question or take a screenshot of the question.</p>
                <p>If you wish to take a screenshot, you are required to go into the settings menu and select 4 points around the question you wish to select. If you are on a managed device (eg. a school computer) you don't need to worry about this.</p>
                <p>Once the screenshot is uploaded, the tool will use AI to explain how to solve the question.</p>
                <p>If you want the tool to provide you with the final answer, simply click the button below and the tool will provide you with the final answer.</p>
                <p>Ensure that the device is connected to the internet and the tool is not in the way of the screenshot.</p>
            </div>
        </div>
    )
}

export default Explaination;
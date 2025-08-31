import React from 'react';
import { RequestType } from '../types/request';
import './RequestTypeDropdown.css';

interface RequestTypeDropdownProps {
  value: RequestType;
  onChange: (value: RequestType) => void;
}

const RequestTypeDropdown: React.FC<RequestTypeDropdownProps> = ({ value, onChange }) => {
  return (
    <div className="dropdown-container">
      <label className="dropdown-label">Solution Type:</label>
      <select 
        className="dropdown-select"
        value={value}
        onChange={(e) => onChange(e.target.value as RequestType)}
      >
        <option value={RequestType.StepByStep}>Step-by-Step Solution</option>
        <option value={RequestType.FinalAnswer}>Final Answer</option>
      </select>
    </div>
  );
};

export default RequestTypeDropdown;

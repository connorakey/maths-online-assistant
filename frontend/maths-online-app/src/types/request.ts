export const RequestType = {
  StepByStep: 'StepByStep',
  FinalAnswer: 'FinalAnswer'
} as const;

export type RequestType = typeof RequestType[keyof typeof RequestType];

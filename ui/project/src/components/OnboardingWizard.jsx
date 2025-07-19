import React, { useState } from 'react';
import WorkspaceStep from './WorkspaceStep';
import DatabaseStep from './DatabaseStep';
import ProgressStep from './ProgressStep';
import SuccessStep from './SuccessStep';

export default function OnboardingWizard() {
  const [step, setStep] = useState(0);
  const [workspace, setWorkspace] = useState(null);
  const [dbJobId, setDbJobId] = useState(null);

  // Step 1: Workspace selection/creation
  const handleWorkspaceSelected = (ws) => {
    setWorkspace(ws);
    setStep(1);
  };

  // Step 2: Database connection
  const handleDatabaseConnected = (jobId) => {
    setDbJobId(jobId);
    setStep(2);
  };

  // Step 3: Progress polling
  const handleOnboardingComplete = () => setStep(3);

  return (
    <div style={{ maxWidth: 500, margin: '0 auto', padding: 24 }}>
      {step === 0 && <WorkspaceStep onNext={handleWorkspaceSelected} />}
      {step === 1 && <DatabaseStep workspace={workspace} onNext={handleDatabaseConnected} />}
      {step === 2 && <ProgressStep jobId={dbJobId} onComplete={handleOnboardingComplete} />}
      {step === 3 && <SuccessStep />}
    </div>
  );
} 
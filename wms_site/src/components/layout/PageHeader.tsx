import React from 'react';
import { pageSubtitle, pageTitle } from './pageStyles';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, action }) => (
  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-8">
    <div>
      <h1 className={pageTitle}>{title}</h1>
      {subtitle && <p className={pageSubtitle}>{subtitle}</p>}
    </div>
    {action}
  </div>
);

export default PageHeader;

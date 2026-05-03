import React from 'react';
import { observer } from 'mobx-react-lite';
import { DashboardStat } from '../models/DashboardModel';
import classNames from 'classnames';

interface DashboardStatsProps {
  stats: DashboardStat[];
}

export const DashboardStats: React.FC<DashboardStatsProps> = observer(({ stats }) => (
  <div className="dashboard-stats grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mb-8">
    {stats.map(stat => (
      <div
        key={stat.label}
        className="dashboard-stats__card bg-white rounded-xl shadow p-5 flex flex-col gap-2"
      >
        <div
          className={classNames(
            'dashboard-stats__icon w-10 h-10 flex items-center justify-center rounded-lg mb-2',
            stat.color
          )}
        >
          <i className={stat.icon + ' text-xl'}></i>
        </div>
        <div className="dashboard-stats__label text-gray-500 text-sm">{stat.label}</div>
        <div className="dashboard-stats__value text-2xl font-bold">{stat.value}</div>
        <div className="dashboard-stats__change flex items-center text-sm">
          <span
            className={classNames(
              stat.changeType === 'up' && 'text-green-600',
              stat.changeType === 'down' && 'text-red-600',
              stat.changeType === 'neutral' && 'text-gray-500',
              'font-semibold mr-1'
            )}
          >
            {stat.changeType === 'up' && <i className="fa-solid fa-arrow-up"></i>}
            {stat.changeType === 'down' && <i className="fa-solid fa-arrow-down"></i>}
            {stat.change}
          </span>
        </div>
      </div>
    ))}
  </div>
));

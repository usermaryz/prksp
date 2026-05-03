import React from 'react';

interface CardProps {
    children: React.ReactNode;
    title?: string;
    subtitle?: string;
    className?: string;
}

const Card: React.FC<CardProps> = ({
    children,
    title,
    subtitle,
    className = '',
}) => {
    return (
        <div className={`bg-white rounded-lg shadow-md border border-gray-200 ${className}`}>
            {(title || subtitle) && (
                <div className="px-6 py-4 border-b border-gray-200">
                    {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
                    {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
                </div>
            )}
            {children}
        </div>
    );
};

export default Card; 
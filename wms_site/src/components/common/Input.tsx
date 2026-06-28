import React from 'react';

interface InputProps {
    type?: 'text' | 'number' | 'email' | 'password';
    value: string;
    onChange: (value: string) => void;
    onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
    placeholder?: string;
    label?: string;
    error?: string;
    disabled?: boolean;
    className?: string;
    required?: boolean;
}

const Input: React.FC<InputProps> = ({
    type = 'text',
    value,
    onChange,
    onKeyDown,
    placeholder,
    label,
    error,
    disabled = false,
    className = '',
    required = false,
}) => {
    return (
        <div className="w-full">
            {label && (
                <label className="block text-sm font-medium text-slate-700 mb-1">
                    {label}
                    {required && <span className="text-red-500 ml-1">*</span>}
                </label>
            )}
            <input
                type={type}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder={placeholder}
                disabled={disabled}
                required={required}
                className={`
          w-full px-4 py-2 rounded-md border
          ${error ? 'border-red-500' : 'border-slate-200'}
          ${disabled ? 'bg-slate-100 cursor-not-allowed' : 'bg-white'}
          focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent rounded-lg
          ${className}
        `}
            />
            {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
        </div>
    );
};

export default Input; 
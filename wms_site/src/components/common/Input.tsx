import React from 'react';

interface InputProps {
    type?: 'text' | 'number' | 'email' | 'password';
    value: string;
    onChange: (value: string) => void;
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
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    {label}
                    {required && <span className="text-red-500 ml-1">*</span>}
                </label>
            )}
            <input
                type={type}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                disabled={disabled}
                required={required}
                className={`
          w-full px-4 py-2 rounded-md border
          ${error ? 'border-red-500' : 'border-gray-300'}
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          ${className}
        `}
            />
            {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
        </div>
    );
};

export default Input; 
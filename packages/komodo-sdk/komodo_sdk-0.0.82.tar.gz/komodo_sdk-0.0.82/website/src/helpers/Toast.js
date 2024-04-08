import toast from 'react-hot-toast';

export const SuccessToast = (message) => {
  return toast.success(message, {
    style: {
      padding: '16px',
      background: '#2E3438',
      color: '#fff',
    }
  });
};
export const ErrorToast = (message) => {
  return toast.error(message, {
    style: {
      padding: '16px',
      background: '#2E3438',
      color: '#fff',
    }
  });
};
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white p-4 mt-auto">
      <div className="container mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div>
            <p>© 2023 BCI Interface</p>
          </div>
          <div className="mt-2 md:mt-0">
            <p>Anushka</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

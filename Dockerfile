FROM dockage/tor-privoxy:latest
LABEL maintainer="trandatdt"
RUN echo "EntryNodes {vn},{jp},{sg},{tw},{hk},{kr},{th}" >> /etc/tor/torrc \
&& echo "ExitNodes {vn},{jp},{sg},{tw},{hk},{kr},{th}" >> /etc/tor/torrc \
&& echo "MaxCircuitDirtiness 15" >> /etc/tor/torrc